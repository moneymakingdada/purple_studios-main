import client from "./client";

export async function createBooking(payload) {
  const { data } = await client.post("/bookings/", payload);
  return data;
}

export async function fetchMyBookings(params = {}) {
  const { data } = await client.get("/bookings/", { params });
  return data.results ?? data;
}

export async function fetchUpcomingBookings() {
  const { data } = await client.get("/bookings/upcoming/");
  return data;
}

export async function cancelBooking(id) {
  const { data } = await client.post(`/bookings/${id}/cancel/`);
  return data;
}

export async function confirmBooking(id) {
  const { data } = await client.post(`/bookings/${id}/confirm/`);
  return data;
}

export async function completeBooking(id) {
  const { data } = await client.post(`/bookings/${id}/complete/`);
  return data;
}

export async function leaveReview(bookingId, rating, comment) {
  const { data } = await client.post("/bookings/reviews/", { booking: bookingId, rating, comment });
  return data;
}

export async function fetchFeaturedReviews() {
  const { data } = await client.get("/bookings/reviews/featured/");
  return data;
}