import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import "./index.css";
import "./styles/ribbon_float.css";
import "./styles/BookingFlow.css";
import "./styles/ServiceDetail.css";
import "./styles/Services.css";
import "./styles/StylistProfile.css";
import "./styles/Stylists.css";
import "./styles/Landing.css";
import "./styles/Register.css";
import "./styles/Navbar.css";
import "./styles/Dashboard.css";
import "./styles/Gallery.css";
import "./styles/stylist/StylistOverview.css";
import "./styles/stylist/StylistAvailability.css";
import "./styles/stylist/StylistCalendar.css";
import "./styles/stylist/StylistLayout.css";


createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
