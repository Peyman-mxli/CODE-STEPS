import React from "react";

function Input({ type = "text", placeholder, value, onChange }) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      style={inputStyle}
    />
  );
}

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

export default Input;