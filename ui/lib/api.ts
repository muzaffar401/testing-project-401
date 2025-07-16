// lib/api.ts

export async function callChatAPI(message: string, conversationId: string) {
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });

    if (!res.ok) {
      const errorText = await res.text(); // Capture error message from backend
      console.error(`Chat API error: ${res.status} - ${errorText}`);
      return null;
    }

    return await res.json();
  } catch (err) {
    console.error("Error sending message:", err);
    return null;
  }
}
