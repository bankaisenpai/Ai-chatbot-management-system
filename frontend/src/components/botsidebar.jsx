export default function BotSidebar({ bots, selected, onSelect }) {
  return (
    <div style={{ width: 200, borderRight: "1px solid #333" }}>
      {bots.map((b) => (
        <div
          key={b.id}
          onClick={() => onSelect(b)}
          style={{
            padding: 10,
            cursor: "pointer",
            background: selected.id === b.id ? "#222" : "transparent",
          }}
        >
          {b.emoji} {b.name}
        </div>
      ))}
    </div>
  );
}
