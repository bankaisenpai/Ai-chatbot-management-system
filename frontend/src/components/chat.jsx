import { useEffect, useRef, useState } from "react";
import { createSession, sendMessage } from "../api";
import { getErrorMessage, isSessionError } from "../api/errors";

export default function Chat({ botId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const bottomRef = useRef(null);
  const sessionIdRef = useRef(null);
  const recognitionRef = useRef(null);

  // Handle bot switch: clear messages, reset session, create new session
  useEffect(() => {
    if (!botId) {
      console.error("[Chat] ERROR: botId is undefined");
      return;
    }

    console.log(`[Chat] Bot ID changed to: ${botId}`);
    
    // Clear previous messages when switching bots
    setMessages([]);
    
    // Reset old session ID
    sessionIdRef.current = null;
    
    console.log(`[Chat] Creating new session for bot_id: ${botId}`);
    
    createSession(botId)
      .then((res) => {
        console.log(`[Chat] Session created: session_id = ${res.session_id}`);
        sessionIdRef.current = res.session_id;
      })
      .catch((err) => {
        console.error(`[Chat] Failed to create session:`, err);
        const errorMsg = getErrorMessage(err);
        setMessages([{ role: "bot", text: `${errorMsg} Please refresh the page.` }]);
      });
  }, [botId]);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Speech Recognition not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setInput(text);
      
      // Only auto-send if session is ready, otherwise user can click Send
      if (text.trim() && sessionIdRef.current) {
        console.log("[Chat] Speech recognized, auto-sending message");
        handleSend(text);
      } else if (text.trim() && !sessionIdRef.current) {
        console.warn("[Chat] Speech recognized but session not ready yet, user can click Send button");
      }
    };

    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  const handleSend = async (textOverride) => {
    const text = textOverride ?? input;
    if (!text.trim() || loading) return;

    if (!botId) {
      console.error("[Chat] ERROR: botId is undefined, cannot send message");
      setMessages((prev) => [...prev, { role: "bot", text: "⚠️ Bot ID missing" }]);
      return;
    }

    if (!sessionIdRef.current) {
      console.warn("[Chat] Session not initialized yet, please wait");
      return;
    }

    console.log(`[Chat] Sending message - bot_id: ${botId}, session_id: ${sessionIdRef.current}`);

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendMessage(
        botId,
        sessionIdRef.current,
        text
      );

      const botReply = res.reply || "…";
      setMessages((prev) => [...prev, { role: "bot", text: botReply }]);

      speak(botReply);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      
      // If session was lost, reset it for retry
      if (isSessionError(err)) {
        console.warn("[Chat] Session error detected, will need to create new session");
        sessionIdRef.current = null;
      }
      
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: errorMsg },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startListening = () => {
    if (recognitionRef.current) {
      setListening(true);
      recognitionRef.current.start();
    }
  };

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#4f46e5" : "#1f2933",
            }}
          >
            {m.text}
          </div>
        ))}

        {loading && <div style={styles.typing}>Bot is typing…</div>}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputBox}>
        <input
          style={styles.input}
          value={input}
          placeholder="Type or speak…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />

        <button style={styles.mic} onClick={startListening}>
          {listening ? "🎙️" : "🎤"}
        </button>

        <button style={styles.button} onClick={() => handleSend()}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { height: "100%", display: "flex", flexDirection: "column" },
  chatBox: {
    flex: 1,
    padding: 10,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  message: {
    maxWidth: "70%",
    padding: 10,
    borderRadius: 10,
    color: "white",
  },
  typing: { color: "#aaa", fontStyle: "italic" },
  inputBox: { display: "flex", padding: 10, gap: 6 },
  input: { flex: 1, padding: 10, borderRadius: 6 },
  button: { padding: "0 16px" },
  mic: { padding: "0 12px", fontSize: 18 },
};
