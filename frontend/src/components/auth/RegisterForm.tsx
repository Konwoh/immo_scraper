import type { FormEvent } from "react";

type RegisterFormProps = {
  username: string;
  password: string;
  error: string | null;
  setUsername: (username: string) => void;
  setPassword: (password: string) => void;
  handleRegistration: (event: FormEvent<HTMLFormElement>) => void;
};

export function RegisterForm({
    username,
    password,
    error,
    setUsername,
    setPassword,
    handleRegistration,
}: RegisterFormProps) {
    return (
        <form onSubmit={handleRegistration} className="auth-form">
            <h1>Registrierung</h1>

            {error && <p className="auth-error">{error}</p>}

            <label>
                E-Mail
                <input
                type="email"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
                />
            </label>

            <label>
                Passwort
                <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                />
            </label>
            <button type="submit">
                Registrieren
            </button>
        </form>

    )
    
}
