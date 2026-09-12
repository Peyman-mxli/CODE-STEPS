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
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f5f5f5"
      }}
    >
      <div
        style={{
          width: "350px",
          padding: "30px",
          backgroundColor: "#fff",
          borderRadius: "10px",
          boxShadow: "0 0 10px rgba(0,0,0,0.1)",
          textAlign: "center"
        }}
      >
        <h2 style={{ marginBottom: "20px" }}>Login</h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{
            width: "100%",
            height: "50px",
            fontSize: "16px",
            marginBottom: "12px",
            padding: "0 10px"
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: "100%",
            height: "50px",
            fontSize: "16px",
            marginBottom: "15px",
            padding: "0 10px"
          }}
        />

        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            height: "50px",
            fontSize: "16px",
            cursor: "pointer",
            marginBottom: "15px"
          }}
        >
          Login
        </button>

        {/* GOOGLE BUTTON SAME WIDTH */}
        <div style={{ width: "100%" }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setMessage("Google Login Failed")}
            width="350"
          />
        </div>

        <p style={{ marginTop: "15px" }}>{message}</p>
      </div>
    </div>
  );
}

export default Login;