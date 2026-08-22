import client from "./client";

// Own profile
export async function fetchMyStylistProfile() {
  const { data } = await client.get("/stylists/me/");
  return data;
}
export async function updateMyStylistProfile(payload) {
  const { data } = await client.patch("/stylists/me/", payload);
  return data;
}

// Availability (recurring weekly windows)
export async function fetchMyAvailability() {
  const { data } = await client.get("/stylists/me/availability/");
  return data.results ?? data;
}
export async function addMyAvailability(payload) {
  const { data } = await client.post("/stylists/me/availability/", payload);
  return data;
}
export async function deleteMyAvailability(id) {
  await client.delete(`/stylists/me/availability/${id}/`);
}

// Time off (one-off blocked dates)
export async function fetchMyTimeOff() {
  const { data } = await client.get("/stylists/me/time-off/");
  return data.results ?? data;
}
export async function addMyTimeOff(payload) {
  const { data } = await client.post("/stylists/me/time-off/", payload);
  return data;
}
export async function deleteMyTimeOff(id) {
  await client.delete(`/stylists/me/time-off/${id}/`);
}

// Booking analytics
export async function fetchBookingStats() {
  const { data } = await client.get("/bookings/stats/");
  return data;
}
