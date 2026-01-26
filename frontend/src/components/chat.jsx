import { useEffect, useRef, useState } from "react";
import { sendMessage } from "../api";
import { getErrorMessage } from "../api/errors";
import "./chat-window.css";

export default function Chat({
  botId,
  sessionId,
  messagesBySession,
  setMessagesBySession,
}) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Web Speech API on mount
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("[Chat] Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      console.log("[Chat] Listening started");
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");

      console.log("[Chat] Transcript:", transcript);
      setInput(transcript);
      setListening(false);
    };

    recognition.onerror = (event) => {
      console.error("[Chat] Speech recognition error:", event.error);
      setListening(false);
    };

    recognition.onend = () => {
      console.log("[Chat] Listening stopped");
      setListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [sessionId, messagesBySession]);

  // DEBUG: Log active session
  useEffect(() => {
    console.log("[Chat] ACTIVE SESSION:", sessionId);
  }, [sessionId]);

  const handleSend = async (textOverride) => {
    const text = textOverride ?? input;
    
    if (!text.trim() || loading) return;
    
    if (!sessionId) {
      console.warn("[Chat] No active session - message not sent");
      return;
    }

    if (!botId) {
      console.warn("[Chat] No botId - message not sent");
      return;
    }

    const userMessage = { id: Date.now(), role: "user", text };
    setInput("");
    setLoading(true);

    try {
      console.log(
        `[Chat] Sending message - bot_id: ${botId}, session_id: ${sessionId}`
      );

      // Add user message to the active session (optimistic update)
      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] || []), userMessage],
      }));

      const res = await sendMessage(botId, sessionId, text);

      const botReply = {
        id: Date.now() + 1,
        role: "bot",
        text: res.reply || "…",
      };
      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] || []), botReply],
      }));
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      console.error("[Chat] Error sending message:", err);

      const errorMessage = {
        id: Date.now() + 2,
        role: "bot",
        text: errorMsg,
      };
      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] || []), errorMessage],
      }));
    } finally {
      setLoading(false);
    }
  };

  const startListening = () => {
    if (!recognitionRef.current) {
      console.warn("[Chat] Speech Recognition not available");
      alert("Speech Recognition not supported in your browser");
      return;
    }

    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      try {
        recognitionRef.current.start();
        console.log("[Chat] Starting speech recognition");
      } catch (err) {
        console.error("[Chat] Error starting recognition:", err);
      }
    }
  };

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
  };

  return (
    <div className="chat-root">
      <div className="chat-header">
        <h3>Chat</h3>
      </div>

      <div className="chat-messages">
        {(() => {
          // Only render if we have an active session
          if (!sessionId) {
            return (
              <div className="chat-empty-state">
                <div className="empty-title">Start a conversation</div>
                <div className="empty-subtitle">Select a chat or send a message to begin</div>
              </div>
            );
          }

          const activeMessages = messagesBySession[sessionId] || [];
          const shouldShowEmpty = activeMessages.length === 0 && !loading;

          return (
            <>
              {shouldShowEmpty && (
                <div className="chat-empty-state">
                  <div className="empty-title">Start a conversation</div>
                  <div className="empty-subtitle">Select a chat or send a message to begin</div>
                </div>
              )}
              {activeMessages.map((m) => (
                <div key={m.id} className={`message ${m.role}`}>
                  {m.text}
                </div>
              ))}
              {loading && <div className="typing-indicator">Bot is typing…</div>}
              <div ref={messagesEndRef} />
            </>
          );
        })()}
      </div>

      <div className="chat-input-box">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={!sessionId}
          placeholder={
            sessionId
              ? "Type a message…"
              : "Create a new chat to start typing"
          }
        />

        <button
          className="chat-mic-btn"
          onClick={startListening}
          disabled={!sessionId}
          title={listening ? "Stop listening" : "Click to speak"}
        >
          {listening ? "🎙️ Listening..." : "🎤"}
        </button>

        <button
          className="chat-send-btn"
          onClick={() => handleSend()}
          disabled={!sessionId || loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
