import { useState } from "react";
import Sidebar from "../components/sidebar.jsx";

export default function ChatPage() {
  const BOT_ID = 1;
  const [sessionId, setSessionId] = useState(
    localStorage.getItem("session_id")
  );

  const handleSelectSession = (id) => {
    if (id) {
      localStorage.setItem("session_id", id);
    } else {
      localStorage.removeItem("session_id");
    }
    setSessionId(id);
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar
        botId={BOT_ID}
        activeSession={sessionId}
        onSelect={handleSelectSession}
      />

      <div style={{ flex: 1 }}>
        {/* Chat UI goes here */}
        {sessionId ? `Session: ${sessionId}` : "Start a new chat"}
      </div>
    </div>
  );
}
