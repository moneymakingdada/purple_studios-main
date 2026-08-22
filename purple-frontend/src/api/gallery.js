import client from "./client";

export async function fetchGallery(params = {}) {
  const { data } = await client.get("/stylists/gallery/", { params });
  return data.results ?? data;
}
