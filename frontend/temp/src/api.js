const API_URL = "http://127.0.0.1:5000";

export async function request(path, options = {}) {
  const token = localStorage.getItem("token");

  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(!isFormData && { "Content-Type": "application/json" }),
  };

  const res = await fetch(API_URL + path, {
    ...options,
    headers,
  });

  try {
    return await res.json();
  } catch (e) {
    return { error: "Server error (no response)" };
  }
}