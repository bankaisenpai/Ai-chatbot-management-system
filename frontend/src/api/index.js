const API_URL = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("token");
}

export async function createSession(botId) {
  const res = await fetch(`${API_URL}/bots/${botId}/sessions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to create session");
  }

  return res.json();
}

export async function sendMessage(botId, sessionId, message) {
  if (!sessionId) {
    throw new Error("Session ID missing");
  }

  const form = new URLSearchParams();
  form.append("message", message);

  const res = await fetch(
    `${API_URL}/bots/${botId}/sessions/${sessionId}/message`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: form,
    }
  );

  if (!res.ok) {
    throw new Error("Message failed");
  }

  return res.json();
}
