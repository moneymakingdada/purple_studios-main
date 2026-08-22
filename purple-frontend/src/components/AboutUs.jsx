/**
 * Static "About Purple" block — reused on Landing and Dashboard.
 * No data fetching needed since the copy is fixed; update it here once
 * and both pages pick up the change.
 */
export default function AboutUs() {
  return (
    <div className="section">
      <div className="split-hero even">
        <div className="about-us-image">
          <img src="https://images.unsplash.com/photo-1522337660859-02fbefca4702?q=80&w=800&auto=format&fit=crop" alt="Purple team" />
        </div>
        <div className="about-us-copy">
          <span className="eyebrow">About Purple</span>
          <h2>Built for Accra, one chair at a time.</h2>
          <p>
            Purple started as a single studio in East Legon with one promise: no more waiting rooms, no more phone tag.
            Every stylist, lash tech, and nail artist on our platform is vetted for craft and consistency.
          </p>
          <p>
            Today we connect thousands of clients across Accra with the right specialist for their hair, skin, and nails —
            booked in minutes, not calls.
          </p>
        </div>
      </div>
    </div>
  );
}
