import { useState } from "react";
import "./sidebar.css";

export default function Sidebar({
  botId,
  onSelectSession,
  onNewChat,
  onDeleteChat,
  activeSessionId,
  sessions,
  setSessions,
}) {
  const formatDate = (dateString) => {
    if (!dateString) return "New Chat";
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return "New Chat";
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year:
          date.getFullYear() !== new Date().getFullYear() ? "numeric" : undefined,
      });
    } catch {
      return "New Chat";
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h4 className="sidebar-title">Chats</h4>
        <button className="new-chat-btn" onClick={onNewChat} title="New Chat">
          +
        </button>
      </div>

      {sessions.length === 0 && (
        <p className="empty-state">No chats yet</p>
      )}

      <div className="sessions-list">
        {sessions.map((s) => {
          const sessionId = s.id || s.session_id;
          return (
            <div
              key={sessionId}
              className={`session-item ${activeSessionId === sessionId ? "active" : ""}`}
            >
              <div
                className="session-content"
                onClick={() => onSelectSession(sessionId)}
              >
                <span className="session-label">Chat</span>
                <small className="session-date">{formatDate(s.created_at)}</small>
              </div>
              <button
                className="session-delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm("Delete this chat?")) {
                    onDeleteChat(sessionId);
                  }
                }}
                title="Delete chat"
              >
                ✕
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
