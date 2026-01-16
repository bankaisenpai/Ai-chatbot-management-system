import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// Auth-specific axios instance (no interceptor needed for auth endpoints)
const authClient = axios.create({
  baseURL: API_URL,
});

export async function login(email, password) {
  console.log("[Auth] Attempting login for:", email);

  try {
    // Create FormData object (required for OAuth2PasswordRequestForm)
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const response = await authClient.post(
      "/auth/login",
      formData
    );

    console.log("[Auth] Login successful, response:", response.data);
    return response.data;
  } catch (error) {
    console.error("[Auth] Login failed:", error.response?.data || error.message);
    throw error;
  }
}

export async function register(email, password) {
  console.log("[Auth] Attempting registration for:", email);

  try {
    const response = await authClient.post(
      "/auth/register",
      {
        email: email,
        password: password,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    console.log("[Auth] Registration successful, response:", response.data);
    return response.data;
  } catch (error) {
    console.error("[Auth] Registration failed:", error.response?.data || error.message);
    throw error;
  }
}

export function getToken() {
  return localStorage.getItem("token");
}

export function setToken(token) {
  localStorage.setItem("token", token);
  console.log("[Auth] Token saved to localStorage");
}

export function clearToken() {
  localStorage.removeItem("token");
  console.log("[Auth] Token cleared from localStorage");
}

export function isAuthenticated() {
  return !!getToken();
}
