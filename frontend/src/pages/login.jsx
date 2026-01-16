import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setToken } from "../api/auth";

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
    <div style={{ maxWidth: "500px", margin: "50px auto", padding: "20px", fontFamily: "Arial" }}>
      <h2>🔐 Login</h2>

      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: "15px" }}>
          <label>Email:</label>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ 
              width: "100%", 
              padding: "10px", 
              boxSizing: "border-box",
              fontSize: "14px"
            }}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label>Password:</label>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ 
              width: "100%", 
              padding: "10px", 
              boxSizing: "border-box",
              fontSize: "14px"
            }}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading} 
          style={{ 
            width: "100%", 
            padding: "12px", 
            fontSize: "16px",
            backgroundColor: loading ? "#cccccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "⏳ Logging in..." : "✓ Login"}
        </button>
      </form>

      {error && (
        <div style={{ 
          color: "#721c24", 
          backgroundColor: "#f8d7da", 
          border: "1px solid #f5c6cb",
          padding: "15px", 
          marginTop: "15px", 
          borderRadius: "4px",
          fontSize: "14px",
          lineHeight: "1.6"
        }}>
          {error}
        </div>
      )}

      {debugInfo && (
        <div style={{ 
          color: "#004085", 
          backgroundColor: "#d1ecf1", 
          border: "1px solid #bee5eb",
          padding: "15px", 
          marginTop: "15px", 
          borderRadius: "4px",
          fontSize: "12px",
          fontFamily: "monospace",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          maxHeight: "200px",
          overflowY: "auto"
        }}>
          DEBUG LOG:
          {"\n" + debugInfo}
        </div>
      )}

      <div style={{ 
        marginTop: "30px", 
        padding: "15px", 
        backgroundColor: "#e7f3ff",
        border: "1px solid #b3d9ff",
        borderRadius: "4px",
        fontSize: "12px"
      }}>
        <strong>Test Credentials:</strong>
        <div>Email: rahul@test.com</div>
        <div>Password: test1234</div>
        <hr/>
        <strong>Debugging Tips:</strong>
        <ul style={{margin: "10px 0", paddingLeft: "20px"}}>
          <li>Open DevTools (F12) → Console to see detailed logs</li>
          <li>Open DevTools → Network to see API requests</li>
          <li>Check if error message contains useful info</li>
          <li>Backend must be running on http://127.0.0.1:8000</li>
        </ul>
      </div>
    </div>
  );
}
