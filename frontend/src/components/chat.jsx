import { useEffect, useRef, useState } from "react";
import { createSession, sendMessage } from "../api";
import "./Chat.css";

export default function Chat({ bot }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const sessionIdRef = useRef(null);

  // Load history per bot
  useEffect(() => {
    const saved = localStorage.getItem(`chat_bot_${bot.id}`);
    setMessages(saved ? JSON.parse(saved) : []);
  }, [bot.id]);

  // Create session when bot changes
  useEffect(() => {
    const startSession = async () => {
      const res = await createSession(bot.id);
      sessionIdRef.current = res.session_id;
    };
    startSession();
  }, [bot.id]);

  // Save history
  useEffect(() => {
    localStorage.setItem(
      `chat_bot_${bot.id}`,
      JSON.stringify(messages)
    );
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || !sessionIdRef.current) return;

    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendMessage(
        bot.id,
        sessionIdRef.current,
        input
      );
      setMessages((m) => [
        ...m,
        { role: "bot", text: res.reply },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "bot", text: "⚠️ API limit hit, try later" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        {bot.emoji} {bot.name}
      </div>

      <div className="chat-box">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`msg ${m.role}`}
          >
            <span className="avatar">
              {m.role === "user" ? "🧑" : bot.emoji}
            </span>
            <span>{m.text}</span>
          </div>
        ))}

        {loading && (
          <div className="msg bot">
            <span className="avatar">{bot.emoji}</span>
            typing…
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message…"
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
