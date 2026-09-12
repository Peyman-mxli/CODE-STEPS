import React, { useState } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function App() {
  const token = localStorage.getItem("token");
  const [showRegister, setShowRegister] = useState(false);

  // ✅ If logged in → show dashboard ONLY
  if (token) return <Dashboard />;

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={{ marginBottom: "20px" }}>CodeSteps 🚀</h1>

        {showRegister ? <Register /> : <Login />}

        <button
          onClick={() => setShowRegister(!showRegister)}
          style={switchButtonStyle}
        >
          {showRegister ? "Go to Login" : "Go to Register"}
        </button>
      </div>
    </div>
  );
}

/* ---------- STYLES ---------- */

const containerStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh"
};

const cardStyle = {
  width: "380px",
  textAlign: "center"
};

const switchButtonStyle = {
  marginTop: "15px",
  width: "100%",
  height: "45px",
  borderRadius: "6px",
  border: "1px solid #ccc",
  backgroundColor: "#f5f5f5",
  cursor: "pointer"
};

export default App;