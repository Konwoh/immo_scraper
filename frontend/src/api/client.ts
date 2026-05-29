const apiHost = import.meta.env.VITE_BASE_URL || window.location.hostname;

export const API_BASE = `http://${apiHost}:8000`;
const SESSION_CHECK_TIMEOUT_MS = 5000;

type ApiFetchOptions = RequestInit & {
  skipAuthRefresh?: boolean;
};

let onAuthExpired: (() => void) | null = null;
let refreshPromise: Promise<boolean> | null = null;

export function setAuthExpiredHandler(handler: (() => void) | null) {
  onAuthExpired = handler;
}

function withCredentials(init: RequestInit): RequestInit {
  return {
    ...init,
    credentials: "include",
  };
}

async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs = SESSION_CHECK_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(input, {
      ...init,
      signal: init.signal ?? controller.signal,
    });
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function refreshSession(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = fetchWithTimeout(`${API_BASE}/token/refresh`, {
      method: "POST",
      credentials: "include",
    })
      .then((response) => response.ok)
      .catch(() => false)
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

export async function restoreSession(): Promise<boolean> {
  try {
    const response = await fetchWithTimeout(`${API_BASE}/auth/session`, {
      credentials: "include",
    });

    if (response.ok) {
      return true;
    }

    if (response.status === 401 || response.status === 403) {
      return refreshSession();
    }

    return false;
  } catch {
    return false;
  }
}

export async function login(username: string, password: string): Promise<void> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetchWithTimeout(`${API_BASE}/login`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Login fehlgeschlagen");
  }
}

export async function logout(): Promise<void> {
  try {
    await fetch(`${API_BASE}/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    return;
  }
}

export async function register(email: string, password: string): Promise<void> {

  const response = await fetchWithTimeout(`${API_BASE}/user`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Registrierung fehlgeschlagen");
  }
}

export async function apiFetch(
  input: RequestInfo | URL,
  init: ApiFetchOptions = {},
): Promise<Response> {
  const { skipAuthRefresh, ...fetchInit } = init;
  const response = await fetch(input, withCredentials(fetchInit));

  if (response.status !== 401 || skipAuthRefresh) {
    return response;
  }

  const refreshed = await refreshSession();
  if (!refreshed) {
    onAuthExpired?.();
    return response;
  }

  const retryResponse = await fetch(input, withCredentials(fetchInit));
  if (retryResponse.status === 401) {
    onAuthExpired?.();
  }

  return retryResponse;
}
