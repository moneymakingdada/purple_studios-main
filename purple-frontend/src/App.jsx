import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";
import StylistRoute from "./components/StylistRoute";
import Landing from "./pages/Landing";
import Services from "./pages/Services";
import ServiceDetail from "./pages/ServiceDetail";
import Stylists from "./pages/Stylists";
import StylistProfile from "./pages/StylistProfile";
import Gallery from "./pages/Gallery";
import BookingFlow from "./pages/BookingFlow";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import StylistLayout from "./pages/stylist/StylistLayout";
import StylistOverview from "./pages/stylist/StylistOverview";
import StylistCalendar from "./pages/stylist/StylistCalendar";
import StylistAvailability from "./pages/stylist/StylistAvailability";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/services" element={<Services />} />
        <Route path="/services/:slug" element={<ServiceDetail />} />
        <Route path="/stylists" element={<Stylists />} />
        <Route path="/stylists/:id" element={<StylistProfile />} />
        <Route path="/gallery" element={<Gallery />} />
        <Route path="/book" element={<BookingFlow />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/portal"
          element={
            <StylistRoute>
              <StylistLayout />
            </StylistRoute>
          }
        >
          <Route index element={<StylistOverview />} />
          <Route path="calendar" element={<StylistCalendar />} />
          <Route path="availability" element={<StylistAvailability />} />
        </Route>
      </Routes>
      <Footer />
    </>
  );
}
