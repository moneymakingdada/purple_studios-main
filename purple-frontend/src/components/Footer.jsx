export default function Footer() {
  return (
    <footer>
      <div className="foot-top">
        <div className="logo">Purple<span>.</span></div>
        <div className="cols">
          <div>
            <h4>Studio</h4>
            <a href="/services">Services</a>
            <a href="/stylists">Stylists</a>
          </div>
          <div>
            <h4>Support</h4>
            <a href="/dashboard">Manage booking</a>
            <a href="mailto:hello@purple.com">Contact</a>
          </div>
        </div>
      </div>
      <div className="foot-bottom">© 2026 Purple Beauty Studio, Accra, Ghana. All rights reserved.</div>
    </footer>
  );
}
