import React, { useState } from "react";
import "./LoginPage.css";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";


function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [attempts, setAttempts] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  // email format validation
  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  };

  // function to set delay
  const delay = (ms) => new Promise((res) => setTimeout(res, ms));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Checks if email is valid before sending to the backend
    if (!validateEmail(email)) {
        setError("Please enter a valid email address.")
        return;
    }

    setIsSubmitting(true);

    // Delay comes into play with too many login attempts
    if (attempts >= 3) {
        await delay(3000); //basic rate limiting delay. Enhance on backend
    }

    // Replace with real login API (backend logic)
    if (email === "user@example.com" && password === "password") {
      navigate("/dashboard");
    } else {
        setAttempts((prev) => prev + 1);
        //keep error vauge to prevent error leaks
        setError("Login failed. Please try again.");
    }

    setIsSubmitting(false)
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} autoComplete="off">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing In..." : "Sign In"}
        </button>
      </form>
      <p className="signup-link">Don't have an account? <Link to="/signup">Sign up here</Link>
      </p>
    </div>
  );
}

export default LoginPage;