import React, { useState } from "react";
import Input from "../components/Input";

function Register() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState("");
  const [avatar, setAvatar] = useState(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    if (password !== confirmPassword) {
      setMessage("Passwords do not match");
      return;
    }

    const formData = new FormData();
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);
    formData.append("username", username);
    formData.append("email", email);
    formData.append("phone", phone);
    formData.append("country", country);
    formData.append("password", password);
    formData.append("confirm_password", confirmPassword);

    if (avatar) {
      formData.append("avatar", avatar);
    }

    try {
      const res = await fetch("http://127.0.0.1:5000/api/register", {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      if (data.message) {
        setMessage("✅ Registered successfully");

        setTimeout(() => {
          window.location.href = "/login";
        }, 1000);
      } else {
        setMessage(data.error || "Register failed");
      }

    } catch {
      setMessage("Server error");
    }
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h2 style={{ marginBottom: "20px" }}>Register</h2>

        <Input placeholder="First Name" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
        <Input placeholder="Last Name" value={lastName} onChange={(e) => setLastName(e.target.value)} />
        <Input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <Input placeholder="Country" value={country} onChange={(e) => setCountry(e.target.value)} />

        <Input type="file" onChange={(e) => setAvatar(e.target.files[0])} />

        <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />

        <button style={buttonStyle} onClick={handleRegister}>
          Register
        </button>

        <p style={{ marginTop: "15px" }}>{message}</p>
      </div>
    </div>
  );
}

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

export default Register;