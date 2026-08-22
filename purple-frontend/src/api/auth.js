import client, { clearTokens, setTokens } from "./client";

export async function login(email, password) {
  const { data } = await client.post("/auth/login/", { email, password });
  setTokens(data);
  return data;
}

export async function register(payload) {
  const { data } = await client.post("/auth/register/", payload);
  return data;
}

export async function fetchMe() {
  const { data } = await client.get("/auth/me/");
  return data;
}

export async function updateMe(payload) {
  const { data } = await client.patch("/auth/me/", payload);
  return data;
}

export function logout() {
  clearTokens();
}
