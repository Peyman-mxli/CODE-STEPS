import React, { useEffect, useState } from "react";
import { request } from "../api";

function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        window.location.href = "/login";
        return;
      }

      const res = await request("/api/user/xp");

      if (res.error) {
        window.location.href = "/login";
      } else {
        setData(res);
      }
    };

    fetchData();
  }, []);

  const handleLogout = async () => {
    await request("/api/logout", { method: "POST" });

    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  if (!data) return <p>Loading dashboard...</p>;

  return (
    <div>
      <h2>Dashboard</h2>

      <p>XP: {data.xp}</p>
      <p>Level: {data.level}</p>
      <p>Rank: {data.rank}</p>

      <br />
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Dashboard;