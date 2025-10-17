// web/src/App.tsx
import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("OD_TOKEN") || "");

  useEffect(() => {
    const t = localStorage.getItem("OD_TOKEN") || "";
    setToken(t);
  }, []);

  function saveToken() {
    localStorage.setItem("OD_TOKEN", token.trim());
    location.reload();
  }
  function clearToken() {
    localStorage.removeItem("OD_TOKEN");
    setToken("");
    location.reload();
  }

  return (
    <>
      <div className="w-full bg-white/5 text-white text-xs px-3 py-2 flex items-center gap-2">
        <span className="opacity-70">API:</span>
        <code className="opacity-80">{import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}</code>
        <span className="ml-4 opacity-70">Token:</span>
        <input
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Paste JWT if API requires auth"
          className="flex-1 bg-black/30 rounded px-2 py-1 outline-none"
        />
        <button onClick={saveToken} className="text-xs bg-white/10 px-2 py-1 rounded">Save</button>
        <button onClick={clearToken} className="text-xs bg-white/10 px-2 py-1 rounded">Clear</button>
      </div>
      <Dashboard />
    </>
  );
}
