import client from "./client";

export async function fetchCategories() {
  const { data } = await client.get("/services/categories/");
  return data.results ?? data;
}

export async function fetchServices(params = {}) {
  const { data } = await client.get("/services/", { params });
  return data.results ?? data;
}

export async function fetchService(slug) {
  const { data } = await client.get(`/services/${slug}/`);
  return data;
}

export async function fetchSalons() {
  const { data } = await client.get("/salons/");
  return data.results ?? data;
}

export async function fetchStylists(params = {}) {
  const { data } = await client.get("/stylists/", { params });
  return data.results ?? data;
}

export async function fetchStylist(id) {
  const { data } = await client.get(`/stylists/${id}/`);
  return data;
}

export async function fetchStylistSlots(stylistId, date, serviceDuration) {
  const { data } = await client.get(`/stylists/${stylistId}/slots/`, {
    params: { date, service_duration: serviceDuration },
  });
  return data;
}
