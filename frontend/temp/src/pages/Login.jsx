import React, { useState } from "react";
import { request } from "../api";
import { GoogleLogin } from "@react-oauth/google";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    const res = await request("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    if (res.access_token) {
      localStorage.setItem("token", res.access_token);

      setMessage("✅ Login successful");

      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    } else {
      setMessage(res.error || "Login failed");
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const token = credentialResponse.credential;

      const res = await fetch("http://127.0.0.1:5000/api/google-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ token })
      });

      const data = await res.json();

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        window.location.href = "/dashboard";
      } else {
        setMessage(data.error || "Google login failed");
      }

    } catch {
      setMessage("Server error");
    }
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h2 style={{ marginBottom: "20px" }}>Login</h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />

        <button style={buttonStyle} onClick={handleLogin}>
          Login
        </button>

        <div style={{ width: "100%", marginTop: "10px" }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setMessage("Google Login Failed")}
            width="100%"
          />
        </div>

        <p style={{ marginTop: "15px" }}>{message}</p>
      </div>
    </div>
  );
}

/* ---------- STYLES ---------- */

const containerStyle = {
  minHeight: "100vh",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  backgroundColor: "#1a1a1a"
};

const cardStyle = {
  width: "400px",
  padding: "30px",
  borderRadius: "12px",
  backgroundColor: "#2a2a2a",
  boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
  textAlign: "center",
  color: "white"
};

const inputStyle = {
  width: "100%",
  padding: "12px",
  margin: "8px 0",
  fontSize: "16px",
  borderRadius: "6px",
  border: "1px solid #444",
  backgroundColor: "#333",
  color: "white"
};

const buttonStyle = {
  width: "100%",
  padding: "12px",
  fontSize: "16px",
  borderRadius: "6px",
  border: "none",
  backgroundColor: "#2563eb",
  color: "white",
  cursor: "pointer",
  marginTop: "10px"
};

export default Login;