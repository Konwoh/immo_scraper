import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [items, setItems] = useState([]);

  // LOGIN
  const login = async () => {
    try {
      // FormData erstellen
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      // Login Request
      const response = await axios.post(
        `${API_BASE}/login`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const accessToken = response.data.access_token;

      localStorage.setItem("token", accessToken);
      setToken(accessToken);

    } catch (error) {
      console.error("Login fehlgeschlagen:", error);
    }
  };

  // ITEMS LADEN
  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API_BASE}/houses/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setItems(response.data);

    } catch (error) {
      console.error("Fehler beim Laden:", error);
    }
  };

  // LOGOUT
  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setItems([]);
  };

  // LOGIN SCREEN
  if (!token) {
    return (
      <div>
        <h1>Login</h1>

        <input
          type="text"
          placeholder="Benutzername"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Passwort"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={login}>
          Einloggen
        </button>
      </div>
    );
  }

  // APP SCREEN
  return (
    <div>
      <h1>Items</h1>

      <button onClick={fetchItems}>
        Items laden
      </button>

      <button onClick={logout}>
        Logout
      </button>

      <table className="table table-hover">
        <thead>
            <tr>
                <th>Titel</th>
                <th>URL</th>
                <th>Immobilien Art</th>
                <th>Preis</th>
                <th>Stadt</th>
                <th>Adresse</th>
            </tr>
        </thead>
        <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.title}</td>
            <td>{item.url}</td>
            <td>{item.estate_type}</td>
            <td>{item.price}</td>
            <td>{item.city}</td>
            <td>{item.address}</td>
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;