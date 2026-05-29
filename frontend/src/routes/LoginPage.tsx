import { useState, type FormEvent } from "react";
import { login } from "@/api/client";
import { LoginForm } from "@/components/auth/LoginForm";
import { Link } from "react-router-dom";

type LoginPageProps = {
  onLoginSuccess: () => void;
};

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(username, password);
      onLoginSuccess();
      setPassword("");
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : "Login fehlgeschlagen",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <LoginForm
        username={username}
        password={password}
        loading={loading}
        error={error}
        setUsername={setUsername}
        setPassword={setPassword}
        handleLogin={handleLogin}
      />
      <Link to="/registration" className="auth-link">Registrieren</Link>
    </>
  );
}
