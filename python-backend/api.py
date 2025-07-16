from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import uuid4
import time
import logging




from main import (
    main_planner_agent,
    nutrition_expert_agent,
    injury_support_agent,
    escalation_agent,
    create_initial_context,
)

from agents import (
    Runner,
    ItemHelpers,
    MessageOutputItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
    InputGuardrailTripwireTriggered,
    Handoff,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration (adjust as needed for deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.choreo.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# =========================
# Models
# =========================

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    content: str
    agent: str

class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[GuardrailCheck] = []

# =========================
# In-memory store for conversation state
# =========================

class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass

class InMemoryConversationStore(ConversationStore):
    _conversations: Dict[str, Dict[str, Any]] = {}

    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._conversations.get(conversation_id)

    def save(self, conversation_id: str, state: Dict[str, Any]):
        self._conversations[conversation_id] = state

# TODO: when deploying this app in scale, switch to your own production-ready implementation
conversation_store = InMemoryConversationStore()

# =========================
# Helpers
# =========================

def _get_agent_by_name(name: str):
    """Return the agent object by name."""
    agents = {
        main_planner_agent.name: main_planner_agent,
        nutrition_expert_agent.name: nutrition_expert_agent,
        injury_support_agent.name: injury_support_agent,
        escalation_agent.name: escalation_agent,
    }
    return agents.get(name, main_planner_agent)

def _get_guardrail_name(g) -> str:
    """Extract a friendly guardrail name."""
    name_attr = getattr(g, "name", None)
    if isinstance(name_attr, str) and name_attr:
        return name_attr
    guard_fn = getattr(g, "guardrail_function", None)
    if guard_fn is not None and hasattr(guard_fn, "__name__"):
        return guard_fn.__name__.replace("_", " ").title()
    fn_name = getattr(g, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name.replace("_", " ").title()
    return str(g)

def _build_agents_list() -> List[Dict[str, Any]]:
    """Build a list of all available agents and their metadata."""
    def make_agent_dict(agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [getattr(h, "agent_name", getattr(h, "name", "")) for h in getattr(agent, "handoffs", [])],
            "tools": [getattr(t, "name", getattr(t, "__name__", "")) for t in getattr(agent, "tools", [])],
            "input_guardrails": [_get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])],
        }
    return [
        make_agent_dict(main_planner_agent),
        make_agent_dict(nutrition_expert_agent),
        make_agent_dict(injury_support_agent),
        make_agent_dict(escalation_agent),
    ]

# =========================
# Main Chat Endpoint
# =========================

from fastapi.responses import JSONResponse
import logging
from uuid import uuid4
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        # Initialize or retrieve conversation state
        is_new = not req.conversation_id or conversation_store.get(req.conversation_id) is None
        if is_new:
            conversation_id: str = uuid4().hex
            ctx = create_initial_context()
            current_agent_name = main_planner_agent.name
            state: Dict[str, Any] = {
                "input_items": [],
                "context": ctx,
                "current_agent": current_agent_name,
            }

            if req.message.strip() == "":
                conversation_store.save(conversation_id, state)
                return ChatResponse(
                    conversation_id=conversation_id,
                    current_agent=current_agent_name,
                    messages=[],
                    events=[],
                    context=ctx.model_dump(),
                    agents=_build_agents_list(),
                    guardrails=[],
                )
        else:
            conversation_id = req.conversation_id
            state = conversation_store.get(conversation_id)
            if not state:
                raise ValueError("Conversation state not found.")

        agent_name = state.get("current_agent")
        if not agent_name:
            raise ValueError("Current agent not found in state.")

        current_agent = _get_agent_by_name(agent_name)
        state["input_items"].append({"content": req.message, "role": "user"})
        old_context = state["context"].model_dump().copy()
        guardrail_checks: List[GuardrailCheck] = []

        # === Run Agent Logic ===
        result = await Runner.run(current_agent, state["input_items"], context=state["context"])

        messages: List[MessageResponse] = []
        events: List[AgentEvent] = []

        for item in result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                messages.append(MessageResponse(content=text, agent=item.agent.name))
                events.append(AgentEvent(
                    id=uuid4().hex,
                    type="message",
                    agent=item.agent.name,
                    content=text
                ))

            elif isinstance(item, HandoffOutputItem):
                events.append(AgentEvent(
                    id=uuid4().hex,
                    type="handoff",
                    agent=item.source_agent.name,
                    content=f"{item.source_agent.name} -> {item.target_agent.name}",
                    metadata={
                        "source_agent": item.source_agent.name,
                        "target_agent": item.target_agent.name
                    },
                ))

                from_agent = item.source_agent
                to_agent = item.target_agent

                ho = next(
                    (h for h in getattr(from_agent, "handoffs", [])
                     if isinstance(h, Handoff) and getattr(h, "agent_name", None) == to_agent.name),
                    None,
                )
                if ho:
                    fn = ho.on_invoke_handoff
                    fv = fn.__code__.co_freevars
                    cl = fn.__closure__ or []
                    if "on_handoff" in fv:
                        idx = fv.index("on_handoff")
                        if idx < len(cl) and cl[idx].cell_contents:
                            cb = cl[idx].cell_contents
                            cb_name = getattr(cb, "__name__", repr(cb))
                            events.append(AgentEvent(
                                id=uuid4().hex,
                                type="tool_call",
                                agent=to_agent.name,
                                content=cb_name
                            ))

                current_agent = item.target_agent

            elif isinstance(item, ToolCallItem):
                tool_name = getattr(item.raw_item, "name", None)
                raw_args = getattr(item.raw_item, "arguments", None)
                tool_args = raw_args
                if isinstance(raw_args, str):
                    try:
                        import json
                        tool_args = json.loads(raw_args)
                    except Exception:
                        pass

                events.append(AgentEvent(
                    id=uuid4().hex,
                    type="tool_call",
                    agent=item.agent.name,
                    content=tool_name or "",
                    metadata={"tool_args": tool_args},
                ))

                if tool_name == "display_workout_selector":
                    messages.append(MessageResponse(
                        content="DISPLAY_WORKOUT_SELECTOR",
                        agent=item.agent.name,
                    ))

            elif isinstance(item, ToolCallOutputItem):
                events.append(AgentEvent(
                    id=uuid4().hex,
                    type="tool_output",
                    agent=item.agent.name,
                    content=str(item.output),
                    metadata={"tool_result": item.output},
                ))

        new_context = state["context"].dict()
        changes = {k: new_context[k] for k in new_context if old_context.get(k) != new_context[k]}
        if changes:
            events.append(AgentEvent(
                id=uuid4().hex,
                type="context_update",
                agent=current_agent.name,
                content="",
                metadata={"changes": changes},
            ))

        state["input_items"] = result.to_input_list()
        state["current_agent"] = current_agent.name
        conversation_store.save(conversation_id, state)

        final_guardrails: List[GuardrailCheck] = []
        for g in getattr(current_agent, "input_guardrails", []):
            name = _get_guardrail_name(g)
            final_guardrails.append(GuardrailCheck(
                id=uuid4().hex,
                name=name,
                input=req.message,
                reasoning="",
                passed=True,
                timestamp=time.time() * 1000,
            ))

        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=current_agent.name,
            messages=messages,
            events=events,
            context=state["context"].dict(),
            agents=_build_agents_list(),
            guardrails=final_guardrails,
        )

    except InputGuardrailTripwireTriggered as e:
        failed = e.guardrail_result.guardrail
        gr_output = e.guardrail_result.output.output_info
        gr_reasoning = getattr(gr_output, "reasoning", "")
        gr_input = req.message
        gr_timestamp = time.time() * 1000
        current_agent = _get_agent_by_name(state["current_agent"])

        guardrail_checks = []
        for g in current_agent.input_guardrails:
            guardrail_checks.append(GuardrailCheck(
                id=uuid4().hex,
                name=_get_guardrail_name(g),
                input=gr_input,
                reasoning=(gr_reasoning if g == failed else ""),
                passed=(g != failed),
                timestamp=gr_timestamp,
            ))

        refusal = "Sorry, I can only answer questions related to health, fitness, and wellness topics."
        state["input_items"].append({"role": "assistant", "content": refusal})

        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=current_agent.name,
            messages=[MessageResponse(content=refusal, agent=current_agent.name)],
            events=[],
            context=state["context"].model_dump(),
            agents=_build_agents_list(),
            guardrails=guardrail_checks,
        )

    except Exception as e:
        logger.exception("Unhandled error in /chat endpoint")
        return JSONResponse(status_code=500, content={"error": str(e)})
