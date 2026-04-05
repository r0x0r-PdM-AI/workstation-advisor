import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthProvider";
import NavBar from "./components/NavBar";

function AdvisorPage() {
  return <div>AdvisorPage</div>;
}

function LoginPage() {
  return <div>LoginPage</div>;
}

function RegisterPage() {
  return <div>RegisterPage</div>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<AdvisorPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
