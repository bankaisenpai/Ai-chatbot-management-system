import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Chat from "../components/chat.jsx";
import BotSidebar from "../components/botsidebar.jsx";
import Sidebar from "../components/sidebar.jsx";
import "../components/dashboard.css";

const bots = [
  { id: 1, name: "Support Bot", emoji: "🛠️" },
  { id: 2, name: "Tutor Bot", emoji: "🎓" },
  { id: 3, name: "Fun Bot", emoji: "🎉" },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeBotId, setActiveBotId] = useState(bots[0].id);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  // Load from localStorage on mount
  const [sessionsByBot, setSessionsByBot] = useState(() => {
    const saved = localStorage.getItem("sessionsByBot");
    return saved ? JSON.parse(saved) : {};
  });
  
  const [messagesBySession, setMessagesBySession] = useState(() => {
    const saved = localStorage.getItem("messagesBySession");
    return saved ? JSON.parse(saved) : {};
  });
  
  const selectedBot = bots.find((b) => b.id === activeBotId) || bots[0];
  const botSessions = sessionsByBot[activeBotId] || [];

  // Auto-save to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem("sessionsByBot", JSON.stringify(sessionsByBot));
  }, [sessionsByBot]);

  useEffect(() => {
    localStorage.setItem("messagesBySession", JSON.stringify(messagesBySession));
  }, [messagesBySession]);

  const handleBotSelect = (bot) => {
    console.log(`[Dashboard] Bot selected: ${bot.name} (id: ${bot.id})`);
    setActiveBotId(bot.id);
    setActiveSessionId(null);
  };

  const handleDeleteChat = (sessionId) => {
    console.log(`[Dashboard] Deleting chat: ${sessionId}`);
    
    // Remove session from sessionsByBot
    setSessionsByBot((prev) => ({
      ...prev,
      [activeBotId]: (prev[activeBotId] || []).filter(
        (s) => (s.id || s.session_id) !== sessionId
      ),
    }));

    // Remove messages for this session
    setMessagesBySession((prev) => {
      const updated = { ...prev };
      delete updated[sessionId];
      return updated;
    });

    // If this was the active session, clear selection
    if (activeSessionId === sessionId) {
      setActiveSessionId(null);
    }
  };

  const handleNewChat = async () => {
    try {
      const token = localStorage.getItem("token");
      console.log(`[Dashboard] Creating session on backend for bot ${activeBotId}`);

      // Create session on backend
      const response = await fetch(
        `http://127.0.0.1:8000/bots/${activeBotId}/sessions`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      const newSession = await response.json();
      console.log(`[Dashboard] Session created on backend:`, newSession.session_id);

      // Normalize: always use session_id from backend
      const normalizedSession = {
        id: newSession.session_id,
        session_id: newSession.session_id,
        conversation_id: newSession.conversation_id,
        created_at: new Date().toISOString(),
      };

      // Add to local state
      setSessionsByBot((prev) => ({
        ...prev,
        [activeBotId]: [normalizedSession, ...(prev[activeBotId] || [])],
      }));

      // THIS IS THE KEY LINE - must be set after session exists
      setActiveSessionId(newSession.session_id);
      setMessagesBySession((prev) => ({
        ...prev,
        [newSession.session_id]: [],
      }));
    } catch (error) {
      console.error("[Dashboard] Failed to create session:", error);
      alert("Failed to create chat session");
    }
  };

  const handleLogout = () => {
    // Clear authentication and chat data
    localStorage.removeItem("token");
    localStorage.removeItem("sessionsByBot");
    localStorage.removeItem("messagesBySession");
    
    console.log("[Dashboard] Logged out successfully");
    navigate("/login");
  };

  return (
    <div className="dashboard">
      <aside className="bot-sidebar">
        <BotSidebar
          bots={bots}
          selected={selectedBot}
          onSelect={handleBotSelect}
        />
        <button className="logout-btn" onClick={handleLogout} title="Sign out">
          🚪 Logout
        </button>
      </aside>

      <aside className="session-sidebar">
        <Sidebar
          botId={activeBotId}
          onSelectSession={(id) => setActiveSessionId(id)}
          onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat}
          activeSessionId={activeSessionId}
          sessions={botSessions}
          setSessions={(updater) => {
            setSessionsByBot((prev) => ({
              ...prev,
              [activeBotId]: updater(prev[activeBotId] || []),
            }));
          }}
        />
      </aside>

      <main className="chat-container">
        <Chat
          botId={activeBotId}
          sessionId={activeSessionId}
          messagesBySession={messagesBySession}
          setMessagesBySession={setMessagesBySession}
        />
      </main>
    </div>
  );
}
