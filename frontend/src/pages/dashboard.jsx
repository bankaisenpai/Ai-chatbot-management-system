import { useState } from "react";
import Chat from "../components/chat";
import BotSidebar from "../components/botsidebar";

const bots = [
  { id: 1, name: "Support Bot", emoji: "🛠️" },
  { id: 2, name: "Tutor Bot", emoji: "🎓" },
  { id: 3, name: "Fun Bot", emoji: "🎉" },
];

export default function Dashboard() {
  const [bot, setBot] = useState(bots[0]);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <BotSidebar
        bots={bots}
        selected={bot}
        onSelect={setBot}
      />
      <Chat bot={bot} />
    </div>
  );
}
