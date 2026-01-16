import { useState } from "react";
import Chat from "../components/chat";
import BotSidebar from "../components/botsidebar";

const bots = [
  { id: 1, name: "Support Bot", emoji: "🛠️" },
  { id: 2, name: "Tutor Bot", emoji: "🎓" },
  { id: 3, name: "Fun Bot", emoji: "🎉" },
];

export default function Dashboard() {
  const [selectedBotId, setSelectedBotId] = useState(bots[0].id);
  const selectedBot = bots.find((b) => b.id === selectedBotId) || bots[0];

  const handleBotSelect = (bot) => {
    console.log(`[Dashboard] Bot selected: ${bot.name} (id: ${bot.id})`);
    setSelectedBotId(bot.id);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <BotSidebar
        bots={bots}
        selected={selectedBot}
        onSelect={handleBotSelect}
      />
      <Chat botId={selectedBotId} />
    </div>
  );
}
