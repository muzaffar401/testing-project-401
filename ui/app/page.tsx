// app/page.tsx

"use client";

import { useEffect, useState, useRef } from "react";
import { AgentPanel } from "@/components/agent-panel";
import { Chat } from "@/components/Chat";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "@/lib/types";
import { callChatAPI } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const msgCounter = useRef(0);

  // Boot the conversation
  useEffect(() => {
    (async () => {
      const data = await callChatAPI("", conversationId ?? "");
      if (!data) {
        console.error("No data returned from chat API");
        return;
      }

      if (!conversationId) setConversationId(data.conversation_id);
      setCurrentAgent(data.current_agent);
      setContext(data.context);
      const initialEvents = (data.events || []).map((e: any, idx: number) => ({
        ...e,
        id: e.id || idx.toString(),
        timestamp: e.timestamp ? new Date(e.timestamp) : new Date(),
      }));
      setEvents(initialEvents);
      setAgents(data.agents || []);
      setGuardrails(data.guardrails || []);
      if (Array.isArray(data.messages)) {
        setMessages(
          data.messages.map((m: any, idx: number) => ({
            id: m.id || idx.toString(),
            content: m.content,
            role: "assistant",
            agent: m.agent,
            timestamp: m.timestamp ? new Date(m.timestamp) : new Date(0),
          }))
        );
      }
    })();
  }, []);

  // Send a user message
  const handleSendMessage = async (content: string) => {
    const userMsg: Message = {
      id: `user-${msgCounter.current++}`,
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const data = await callChatAPI(content, conversationId ?? "");
    if (!data) {
      console.error("No data returned from chat API");
      setIsLoading(false);
      return;
    }

    if (!conversationId) setConversationId(data.conversation_id);
    setCurrentAgent(data.current_agent);
    setContext(data.context);

    if (data.events) {
      const stamped = data.events.map((e: any, idx: number) => ({
        ...e,
        id: e.id || idx.toString(),
        timestamp: e.timestamp ? new Date(e.timestamp) : new Date(),
      }));
      setEvents((prev) => [...prev, ...stamped]);
    }

    if (data.agents) setAgents(data.agents);
    if (data.guardrails) setGuardrails(data.guardrails);

    if (data.messages) {
      const responses: Message[] = data.messages.map((m: any, idx: number) => ({
        id: m.id || `assistant-${msgCounter.current++}`,
        content: m.content,
        role: "assistant",
        agent: m.agent,
        timestamp: m.timestamp ? new Date(m.timestamp) : new Date(0),
      }));
      setMessages((prev) => [...prev, ...responses]);
    }

    setIsLoading(false);
  };

  return (
    <main className="flex h-screen gap-2 bg-gradient-to-br from-green-50 to-blue-50 p-2">
      <AgentPanel
        agents={agents}
        currentAgent={currentAgent}
        events={events}
        guardrails={guardrails}
        context={context}
      />
      <Chat
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </main>
  );
}
