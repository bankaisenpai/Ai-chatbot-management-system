import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setToken } from "../api/auth";
import "../Pages/login.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("rahul@test.com");
  const [password, setPassword] = useState("test1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setDebugInfo("Starting login...");

    try {
      console.log("[Login] Email:", email, "Password:", password);
      setDebugInfo("1. Sending login request...");
      
      if (!email || !password) {
        throw new Error("Email and password are required");
      }
      
      const data = await login(email, password);
      
      setDebugInfo("2. Login response received: " + JSON.stringify(data));
      console.log("[Login] Response data:", data);
      
      if (!data) {
        throw new Error("No response from server");
      }
      
      if (!data.access_token) {
        throw new Error("No token in response. Response was: " + JSON.stringify(data));
      }
      
      setDebugInfo("3. Token received: " + data.access_token.substring(0, 30) + "...");
      setToken(data.access_token);
      
      setDebugInfo("4. Token saved to localStorage");
      const savedToken = localStorage.getItem("token");
      console.log("[Login] Token in localStorage:", savedToken ? "YES" : "NO");
      
      setDebugInfo("5. Redirecting to dashboard...");
      console.log("[Login] Navigating to /dashboard");
      navigate("/dashboard");
      
    } catch (error) {
      console.error("[Login] Full error:", error);
      console.error("[Login] Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers,
      });
      
      const errorMsg = 
        error.response?.data?.detail || 
        error.message || 
        "Login failed";
      setError(`❌ Login failed: ${errorMsg}`);
      setDebugInfo("ERROR: " + errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    
  
    <div className="login-card">
      <h1>Welcome Back 👋</h1>
      <p className="subtitle">Sign in to continue</p>

      <form onSubmit={handleLogin}>
  <label>Email</label>
  <input
    type="email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    placeholder="you@example.com"
    required
  />

  <label>Password</label>
  <input
    type="password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
    placeholder="••••••••"
    required
  />

  <button type="submit" disabled={loading}>
    {loading ? "⏳ Logging in..." : "Login"}
  </button>

  {error && (
    <div className="login-error">
      {error}
    </div>
  )}
</form>
</div>
  );
}
