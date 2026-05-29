import { useState, type FormEvent } from "react";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { register } from "@/api/client";
import { useNavigate } from "react-router-dom";

export function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleRegistration = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    try {
      await register(username, password);
      navigate("/")
    } catch (registerError) {
      setError(
        registerError instanceof Error
          ? registerError.message
          : "Registrierung fehlgeschlagen",
      );
    }
  };

  return (
    <RegisterForm
      username={username}
      password={password}
      error={error}
      setUsername={setUsername}
      setPassword={setPassword}
      handleRegistration={handleRegistration}
    />
  );
}