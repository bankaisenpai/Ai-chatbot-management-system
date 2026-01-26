import axios from "axios";

const API = "http://127.0.0.1:8000";

export const getSessions = async (botId, token) => {
  const res = await axios.get(`${API}/bots/${botId}/sessions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.data;
};
