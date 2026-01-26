import "./botsidebar.css";

export default function BotSidebar({ bots, selected, onSelect }) {
  return (
    <div className="bots-sidebar-container">
      <h4 className="bots-title">Bots</h4>
      <div className="bots-list">
        {bots.map((b) => (
          <div
            key={b.id}
            className={`bot-item ${selected?.id === b.id ? "active" : ""}`}
            onClick={() => onSelect(b)}
          >
            <span className="bot-emoji">{b.emoji}</span>
            <span className="bot-name">{b.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
