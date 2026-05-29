import type { FormEvent } from "react";

type LoginFormProps = {
  username: string;
  password: string;
  loading: boolean;
  error: string | null;
  setUsername: (username: string) => void;
  setPassword: (password: string) => void;
  handleLogin: (event: FormEvent<HTMLFormElement>) => void | Promise<void>;
};

export function LoginForm({
    username,
    password,
    loading,
    error,
    setUsername,
    setPassword,
    handleLogin,
}: LoginFormProps) {
    return (
        <form className="auth-form" onSubmit={handleLogin}>
            <h1>Login</h1>

            {error && <p className="auth-error">{error}</p>}

            <label>
              E-Mail
              <input
                type="email"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />
            </label>

            <label>
              Passwort
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Einloggen..." : "Einloggen"}
            </button>
        </form>
    )
}
