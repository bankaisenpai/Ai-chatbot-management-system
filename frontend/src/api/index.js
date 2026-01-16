import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
});

// Axios interceptor to add Bearer token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("[API] Bearer token added to request");
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log("[API] Response successful:", response.status);
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error("[API] Unauthorized - token may be invalid");
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export async function createSession(botId) {
  if (!botId) {
    console.error("[API] ERROR: botId is undefined when creating session");
    throw new Error("Bot ID is missing. Cannot create session.");
  }

  console.log(`[API] Creating session for bot_id: ${botId}`);

  try {
    const response = await apiClient.post(`/bots/${botId}/sessions`);
    console.log(`[API] Session created successfully:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`[API] Failed to create session:`, error.message);
    throw error;
  }
}

export async function sendMessage(botId, sessionId, message) {
  if (!botId) {
    console.error("[API] ERROR: botId is undefined when sending message");
    throw new Error("Bot ID is missing. Cannot send message.");
  }

  if (!sessionId) {
    console.error("[API] ERROR: sessionId is undefined when sending message");
    throw new Error("Session ID missing. Please create a session first.");
  }

  console.log(`[API] Sending message - bot_id: ${botId}, session_id: ${sessionId}, message: ${message}`);

  try {
    // Use FormData for multipart/form-data encoding (required by FastAPI Form(...))
    const formData = new FormData();
    formData.append("message", message);

    const response = await apiClient.post(
      `/bots/${botId}/sessions/${sessionId}/message`,
      formData
    );
    console.log(`[API] Message sent successfully:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`[API] Message failed:`, error.message);
    console.error(`[API] Error response:`, error.response?.data);
    throw error;
  }
}
