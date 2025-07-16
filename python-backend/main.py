from __future__ import annotations as _annotations

import random
from pydantic import BaseModel, ConfigDict
import string
from dotenv import load_dotenv
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    function_tool,
    handoff,
    GuardrailFunctionOutput,
    input_guardrail,
    set_default_openai_api
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

import os

# =========================
# CONTEXT
# =========================
load_dotenv()

set_default_openai_api(api=os.getenv("OPENAI_API_KEY"))

class UserSessionContext(BaseModel):
    name: str | None = None
    uid: int | None = None
    goal: Optional[Dict] = None
    diet_preferences: Optional[str] = None
    workout_plan: Optional[Dict] = None
    meal_plan: Optional[List[str]] = None
    injury_notes: Optional[str] = None
    handoff_logs: List[str] = []
    progress_logs: List[Dict[str, str]] = []

def create_initial_context() -> UserSessionContext:
    ctx = UserSessionContext()
    ctx.uid = random.randint(100000, 999999)
    ctx.name = None  # Now agent will prompt for name
    return ctx

# =========================
# TOOLS
# =========================

class GoalStructure(BaseModel):
    objective: str
    quantity: float
    metric: str
    duration: str
    priority: str

    model_config = ConfigDict(extra='forbid')

@function_tool(
    name_override="goal_analyzer_tool",
    description_override="Analyze user health goals and convert them into structured format."
)
async def goal_analyzer_tool(
    context: RunContextWrapper[UserSessionContext], 
    user_goal: str
) -> str:
    # Analyze the user's actual goal input
    goal_lower = user_goal.lower()
    
    # Extract goal components from user input
    if "lose" in goal_lower or "weight loss" in goal_lower:
        objective = "weight loss"
    elif "gain" in goal_lower or "muscle" in goal_lower:
        objective = "muscle gain"
    elif "run" in goal_lower or "cardio" in goal_lower:
        objective = "cardio fitness"
    else:
        objective = "general fitness"
    
    # Extract quantity and metric
    import re
    quantity_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|pounds|lbs|km|miles)', goal_lower)
    if quantity_match:
        quantity = float(quantity_match.group(1))
        metric = quantity_match.group(2)
    else:
        quantity = 5.0
        metric = "kg"
    
    # Extract duration
    duration_match = re.search(r'(\d+)\s*(month|week|day)s?', goal_lower)
    if duration_match:
        duration_num = int(duration_match.group(1))
        duration_unit = duration_match.group(2)
        duration = f"{duration_num} {duration_unit}{'s' if duration_num > 1 else ''}"
    else:
        duration = "2 months"
    
    goal_data = {
        "objective": objective,
        "quantity": quantity,
        "metric": metric, 
        "duration": duration,
        "priority": "high"
    }
    context.context.goal = goal_data
    return f"Goal analyzed and structured: {json.dumps(goal_data, indent=2)}"

@function_tool(
    name_override="meal_planner_tool",
    description_override="Generate a 7-day meal plan based on dietary preferences and health goals."
)
async def meal_planner_tool(
    context: RunContextWrapper[UserSessionContext],
    dietary_preferences: str
) -> str:
    context.context.diet_preferences = dietary_preferences
    
    # Create personalized meal plans based on dietary preferences
    dietary_lower = dietary_preferences.lower()
    
    if "diabetic" in dietary_lower or "diabetes" in dietary_lower:
        meal_plan = [
            "Day 1: Steel-cut oatmeal with berries and almonds (low glycemic)",
            "Day 2: Grilled chicken breast with quinoa and steamed broccoli",
            "Day 3: Baked salmon with roasted vegetables and brown rice",
            "Day 4: Lentil soup with whole grain bread and mixed greens",
            "Day 5: Greek yogurt with honey and low-sugar granola",
            "Day 6: Turkey and avocado sandwich on whole grain bread",
            "Day 7: Vegetable stir-fry with brown rice and tofu"
        ]
        context.context.meal_plan = meal_plan
        return f"7-day diabetic-friendly meal plan generated:\n" + "\n".join(meal_plan)
    
    elif "vegetarian" in dietary_lower:
        meal_plan = [
            "Day 1: Oatmeal with berries, nuts, and chia seeds",
            "Day 2: Quinoa salad with chickpeas, vegetables, and tahini dressing",
            "Day 3: Lentil curry with brown rice and steamed vegetables",
            "Day 4: Vegetable soup with whole grain bread and mixed greens",
            "Day 5: Greek yogurt with honey, granola, and fresh fruit",
            "Day 6: Hummus and avocado sandwich on whole grain bread",
            "Day 7: Vegetable stir-fry with tofu and brown rice"
        ]
        context.context.meal_plan = meal_plan
        return f"7-day vegetarian meal plan generated:\n" + "\n".join(meal_plan)
    
    elif "keto" in dietary_lower or "low-carb" in dietary_lower:
        meal_plan = [
            "Day 1: Scrambled eggs with avocado and spinach",
            "Day 2: Grilled chicken with cauliflower rice and broccoli",
            "Day 3: Baked salmon with roasted asparagus",
            "Day 4: Beef stir-fry with zucchini noodles",
            "Day 5: Greek yogurt with berries and nuts",
            "Day 6: Turkey and cheese roll-ups with cucumber",
            "Day 7: Vegetable omelette with mushrooms and cheese"
        ]
        context.context.meal_plan = meal_plan
        return f"7-day keto/low-carb meal plan generated:\n" + "\n".join(meal_plan)
    
    else:
        # General balanced meal plan
        meal_plan = [
            "Day 1: Oatmeal with berries and nuts",
            "Day 2: Grilled chicken salad with quinoa",
            "Day 3: Salmon with steamed vegetables",
            "Day 4: Lentil soup with whole grain bread",
            "Day 5: Greek yogurt with honey and granola",
            "Day 6: Turkey and avocado sandwich",
            "Day 7: Vegetable stir-fry with brown rice"
        ]
        context.context.meal_plan = meal_plan
        return f"7-day balanced meal plan generated for {dietary_preferences} diet:\n" + "\n".join(meal_plan)

@function_tool(
    name_override="workout_recommender_tool",
    description_override="Suggest workout plan based on parsed goals and experience level."
)
async def workout_recommender_tool(
    context: RunContextWrapper[UserSessionContext],
    experience_level: str
) -> str:
    # Consider injury notes when creating workout plan
    injury_notes = context.context.injury_notes or ""
    injury_lower = injury_notes.lower()
    
    # Check for knee pain or other injuries
    if "knee" in injury_lower or "knee pain" in injury_lower:
        workout_plan = {
            "type": "low_impact_strength_training",
            "frequency": "3 times per week",
            "duration": "45 minutes",
            "notes": "Knee-friendly exercises focusing on upper body and core",
            "exercises": [
                "Seated shoulder press: 3 sets x 12 reps",
                "Bicep curls: 3 sets x 12 reps",
                "Tricep dips: 3 sets x 10 reps",
                "Planks: 3 sets x 30 seconds",
                "Seated leg extensions: 3 sets x 15 reps",
                "Straight-leg raises: 3 sets x 12 reps each leg",
                "Swimming or cycling (low-impact cardio): 20 minutes"
            ],
            "avoid": ["Squats", "Lunges", "Jumping exercises", "High-impact cardio"]
        }
    elif "back" in injury_lower or "back pain" in injury_lower:
        workout_plan = {
            "type": "core_focused_strength_training",
            "frequency": "3 times per week",
            "duration": "40 minutes",
            "notes": "Back-friendly exercises with focus on core stability",
            "exercises": [
                "Bird dogs: 3 sets x 10 reps each side",
                "Cat-cow stretches: 3 sets x 10 reps",
                "Pelvic tilts: 3 sets x 15 reps",
                "Wall push-ups: 3 sets x 12 reps",
                "Seated rows: 3 sets x 12 reps",
                "Gentle walking: 20 minutes",
                "Yoga or stretching: 15 minutes"
            ],
            "avoid": ["Heavy lifting", "Twisting movements", "High-impact exercises"]
        }
    else:
        # Standard workout based on experience level
        if "beginner" in experience_level.lower():
            workout_plan = {
                "type": "beginner_strength_training",
                "frequency": "3 times per week",
                "duration": "30 minutes",
                "notes": "Beginner-friendly exercises with proper form focus",
                "exercises": [
                    "Bodyweight squats: 3 sets x 10 reps",
                    "Wall push-ups: 3 sets x 8 reps",
                    "Planks: 3 sets x 20 seconds",
                    "Walking: 20 minutes",
                    "Stretching: 10 minutes"
                ]
            }
        elif "advanced" in experience_level.lower():
            workout_plan = {
                "type": "advanced_strength_training",
                "frequency": "4 times per week",
                "duration": "60 minutes",
                "notes": "Advanced exercises with progressive overload",
                "exercises": [
                    "Barbell squats: 4 sets x 8 reps",
                    "Bench press: 4 sets x 8 reps",
                    "Deadlifts: 3 sets x 6 reps",
                    "Pull-ups: 3 sets x 8 reps",
                    "Planks: 3 sets x 60 seconds",
                    "Cardio intervals: 20 minutes"
                ]
            }
        else:
            # Intermediate level
            workout_plan = {
                "type": "intermediate_strength_training",
                "frequency": "3 times per week",
                "duration": "45 minutes",
                "notes": "Balanced strength and cardio program",
                "exercises": [
                    "Squats: 3 sets x 12 reps",
                    "Push-ups: 3 sets x 10 reps",
                    "Planks: 3 sets x 30 seconds",
                    "Lunges: 3 sets x 10 reps each leg",
                    "Moderate cardio: 25 minutes"
                ]
            }
    
    context.context.workout_plan = workout_plan
    return f"Workout plan for {experience_level} level:\n{json.dumps(workout_plan, indent=2)}"

@function_tool(
    name_override="checkin_scheduler_tool",
    description_override="Schedule recurring weekly progress checks."
)
async def checkin_scheduler_tool(
    context: RunContextWrapper[UserSessionContext]
) -> str:
    next_checkin = datetime.now() + timedelta(days=7)
    log_entry = {
        "date": datetime.now().isoformat(),
        "type": "checkin_scheduled",
        "next_checkin": next_checkin.isoformat()
    }
    context.context.progress_logs.append(log_entry)
    return f"Progress check-in scheduled for {next_checkin.strftime('%Y-%m-%d')}"

@function_tool(
    name_override="progress_tracker_tool",
    description_override="Accept updates, track user progress, modify session context."
)
async def progress_tracker_tool(
    context: RunContextWrapper[UserSessionContext],
    progress_update: str,
    metric_value: float
) -> str:
    log_entry = {
        "date": datetime.now().isoformat(),
        "update": progress_update,
        "metric_value": metric_value
    }
    context.context.progress_logs.append(log_entry)
    return f"Progress logged: {progress_update} - Value: {metric_value}"

@function_tool(
    name_override="set_user_name",
    description_override="Set the user's name in the session context."
)
async def set_user_name(
    context: RunContextWrapper[UserSessionContext],
    name: str
) -> str:
    greetings = [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
        "hy", "hii", "helo", "hey there"
    ]
    name_clean = name.strip().lower()
    if name_clean in greetings or any(name_clean.startswith(g) for g in greetings):
        return "I'm here to help you! Could you please tell me your actual name so I can personalize your experience?"
    context.context.name = name
    return f"Name set to {name}."

# =========================
# HOOKS
# =========================

async def on_nutrition_expert_handoff(context: RunContextWrapper[UserSessionContext]) -> None:
    context.context.handoff_logs.append(f"Handed off to Nutrition Expert at {datetime.now().isoformat()}")
    if not context.context.diet_preferences:
        context.context.diet_preferences = "general"

async def on_injury_support_handoff(context: RunContextWrapper[UserSessionContext]) -> None:
    context.context.handoff_logs.append(f"Handed off to Injury Support at {datetime.now().isoformat()}")
    if not context.context.injury_notes:
        context.context.injury_notes = "No specific injury noted"

async def on_escalation_handoff(context: RunContextWrapper[UserSessionContext]) -> None:
    context.context.handoff_logs.append(f"Escalated to human coach at {datetime.now().isoformat()}")

# =========================
# GUARDRAILS
# =========================

class GoalValidationOutput(BaseModel):
    reasoning: str
    is_valid: bool
    structured_goal: Optional[GoalStructure] = None

    model_config = ConfigDict(extra='forbid')

class HealthRelevanceOutput(BaseModel):
    reasoning: str
    is_relevant: bool

    model_config = ConfigDict(extra='forbid')

goal_validation_agent = Agent(
    model="gpt-4o-mini",
    name="Goal Validation Guardrail",
    instructions=(
        "Validate if the user's health goal input follows the required format: quantity, metric, duration. "
        "Examples of valid goals: 'lose 5kg in 2 months', 'build muscle in 3 months', 'run 5km in 4 weeks'. "
        "Return is_valid=True if the goal has clear quantity, metric, and duration, else False. "
        "If valid, provide structured_goal with objective, quantity, metric, and duration fields."
    ),
    output_type=GoalValidationOutput,
)

@input_guardrail(name="Goal Validation Guardrail")
async def goal_validation_guardrail(
    context: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(goal_validation_agent, input, context=context.context)
    final = result.final_output_as(GoalValidationOutput)
    # Do NOT tripwire, just provide info
    return GuardrailFunctionOutput(output_info=final, tripwire_triggered=False)

health_relevance_agent = Agent(
    name="Health Relevance Guardrail",
    model="gpt-4o-mini",
    instructions=(
        "Determine if the user's message is related to health, fitness, nutrition, wellness, or medical topics. "
        "Return is_relevant=True if it is health-related, else False, with brief reasoning."
    ),
    output_type=HealthRelevanceOutput,
)

@input_guardrail(name="Health Relevance Guardrail")
async def health_relevance_guardrail(
    context: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    user_message = input if isinstance(input, str) else (input[-1]['content'] if input and isinstance(input[-1], dict) else "")
    greetings = [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
        "hy", "hii", "helo", "hey there"
    ]
    onboarding_phrases = [
        "my name is", "i am", "call me", "it's", "im ", "i’m "
    ]
    user_message_clean = user_message.strip().lower()
    if (
        any(user_message_clean.startswith(g) for g in greetings)
        or any(user_message_clean.startswith(p) for p in onboarding_phrases)
    ):
        return GuardrailFunctionOutput(
            output_info=HealthRelevanceOutput(reasoning="Greeting or onboarding message, always allowed.", is_relevant=True),
            tripwire_triggered=False
        )
    # Otherwise, run the normal relevance check
    result = await Runner.run(health_relevance_agent, input, context=context.context)
    final = result.final_output_as(HealthRelevanceOutput)
    return GuardrailFunctionOutput(output_info=final, tripwire_triggered=not final.is_relevant)

# =========================
# AGENTS (unchanged, omitted here to save space)
# =========================
# Keep all agent definitions and handoff setup as in previous code.


# =========================
# AGENTS
# =========================

# Handlers for handoffs
async def on_nutrition_expert_handoff(context: RunContextWrapper[UserSessionContext]):
    context.context.handoff_logs.append(f"Handed off to Nutrition Expert at {datetime.now().isoformat()}")
    if not context.context.diet_preferences:
        context.context.diet_preferences = "general"

async def on_injury_support_handoff(context: RunContextWrapper[UserSessionContext]):
    context.context.handoff_logs.append(f"Handed off to Injury Support at {datetime.now().isoformat()}")
    if not context.context.injury_notes:
        context.context.injury_notes = "No specific injury noted"

async def on_escalation_handoff(context: RunContextWrapper[UserSessionContext]):
    context.context.handoff_logs.append(f"Escalated to human coach at {datetime.now().isoformat()}")

def main_planner_instructions(run_context: RunContextWrapper[UserSessionContext], agent: Agent[UserSessionContext], last_user_message: str = None) -> str:
    ctx = run_context.context
    greetings = [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
        "hy", "hii", "helo", "hey there"
    ]
    if not ctx.name and last_user_message and any(last_user_message.strip().lower().startswith(g) for g in greetings):
        return (
            "Hello! I'm your Health & Wellness Planner Agent. "
            "I'll help you set and achieve your health and fitness goals. "
            "Let's get started! What's your name?"
        )
    if not ctx.name:
        return "Welcome! What's your name?"
    if not ctx.goal:
        return f"Hi {ctx.name}! What is your main fitness or health goal? (e.g., lose 5kg in 2 months, run a 5k, build muscle, etc.)"
    # Build comprehensive context information
    name = ctx.name or "User"
    context_info = []
    
    if ctx.goal:
        goal_info = f"Goal: {ctx.goal.get('objective', 'unknown')} - {ctx.goal.get('quantity', 0)} {ctx.goal.get('metric', 'units')} in {ctx.goal.get('duration', 'unknown time')}"
        context_info.append(goal_info)
    
    if ctx.diet_preferences:
        context_info.append(f"Dietary preferences: {ctx.diet_preferences}")
    
    if ctx.injury_notes:
        context_info.append(f"Injury considerations: {ctx.injury_notes}")
    
    if ctx.workout_plan:
        context_info.append(f"Current workout plan: {ctx.workout_plan.get('type', 'unknown')} - {ctx.workout_plan.get('frequency', 'unknown frequency')}")
    
    if ctx.meal_plan:
        context_info.append(f"Meal plan: {len(ctx.meal_plan)} days planned")
    
    context_summary = "\n".join(context_info) if context_info else "No specific context set yet"
    
    return f"""{RECOMMENDED_PROMPT_PREFIX}
You are a Health & Wellness Planner Agent for {name}.

Current Context:
{context_summary}

Your role is to:
1. Help users set and achieve health goals
2. Provide personalized meal and workout plans
3. Consider dietary restrictions and injuries
4. Track progress and provide motivation
5. Hand off to specialized agents when needed


When a user mentions:
- Dietary restrictions (diabetic, vegetarian, etc.) → Use meal_planner_tool
- Injuries or pain → Consider injury_support_agent handoff
- Complex nutrition needs → Consider nutrition_expert_agent handoff
- Need for human trainer → Consider escalation_agent handoff

Always maintain context continuity and provide personalized responses based on the user's specific situation.
"""

main_planner_agent = Agent[UserSessionContext](
    name="Health & Wellness Planner",
    model="gpt-4o",
    handoff_description="Helps users with goal setting, meal plans, workouts, and tracking.",
    instructions=main_planner_instructions,
    tools=[set_user_name, goal_analyzer_tool,checkin_scheduler_tool, progress_tracker_tool],
    input_guardrails=[goal_validation_guardrail, health_relevance_guardrail],
)

def nutrition_expert_instructions(run_context: RunContextWrapper[UserSessionContext], agent: Agent[UserSessionContext]) -> str:
    ctx = run_context.context
    return f"{RECOMMENDED_PROMPT_PREFIX}\nYou are a Nutrition Expert helping with dietary plans for {ctx.diet_preferences or 'general'} needs."

def injury_support_instructions(run_context: RunContextWrapper[UserSessionContext], agent: Agent[UserSessionContext]) -> str:
    ctx = run_context.context
    return f"{RECOMMENDED_PROMPT_PREFIX}\nYou are an Injury Support Agent. Notes: {ctx.injury_notes or 'none'}"

def escalation_agent_instructions(run_context: RunContextWrapper[UserSessionContext], agent: Agent[UserSessionContext]) -> str:
    ctx = run_context.context
    return f"{RECOMMENDED_PROMPT_PREFIX}\nYou handle escalations to human trainers for {ctx.name}."

nutrition_expert_agent = Agent[UserSessionContext](
    name="Nutrition Expert Agent",
    model="gpt-4.1",
    handoff_description="Helps with complex dietary needs.",
    instructions=nutrition_expert_instructions,
    tools=[meal_planner_tool, progress_tracker_tool],
    input_guardrails=[health_relevance_guardrail],
)

injury_support_agent = Agent[UserSessionContext](
    name="Injury Support Agent",
    model="gpt-4.1",
    handoff_description="Supports injury recovery and exercise modifications.",
    instructions=injury_support_instructions,
    tools=[workout_recommender_tool, progress_tracker_tool],
    input_guardrails=[health_relevance_guardrail],
)

escalation_agent = Agent[UserSessionContext](
    name="Escalation Agent",
    model="gpt-4.1",
    handoff_description="Handles human coach requests.",
    instructions=escalation_agent_instructions,
    tools=[progress_tracker_tool],
    input_guardrails=[health_relevance_guardrail],
)

main_planner_agent.handoffs = [
    handoff(agent=nutrition_expert_agent, on_handoff=on_nutrition_expert_handoff),
    handoff(agent=injury_support_agent, on_handoff=on_injury_support_handoff),
    handoff(agent=escalation_agent, on_handoff=on_escalation_handoff),
]

nutrition_expert_agent.handoffs = [main_planner_agent]
injury_support_agent.handoffs = [main_planner_agent]
escalation_agent.handoffs = [main_planner_agent]
