// Fallback stock imagery keyed by category, used whenever a Service has no uploaded image yet.
const CATEGORY_IMAGES = {
  "men's cuts": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=700&auto=format&fit=crop",
  "women's styling": "https://images.unsplash.com/photo-1522337660859-02fbefca4702?q=80&w=700&auto=format&fit=crop",
  "lash studio": "https://images.unsplash.com/photo-1583001809873-a128495da465?q=80&w=700&auto=format&fit=crop",
  "nails & pedicure": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?q=80&w=700&auto=format&fit=crop",
};

const DEFAULT_IMAGE = "https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=700&auto=format&fit=crop";

export function getServiceImage(service) {
  if (service?.image) return service.image;
  const key = service?.category_name?.toLowerCase?.();
  return CATEGORY_IMAGES[key] || DEFAULT_IMAGE;
}
