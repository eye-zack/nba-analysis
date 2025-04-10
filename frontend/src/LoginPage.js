// This component handles the login process, including form validation, sanitization of user inputs, and communication with the backend for authentication.
// After successful login, the user is redirected to the dashboard. If there's an error, it shows an error message.

import React, { useState } from "react";
import "./LoginPage.css";
import { useNavigate, Link } from "react-router-dom";

function LoginPage() {
  // manage form data
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [attempts, setAttempts] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  // mitigates XSS attacks by sanitizing input
  const sanitizeInput = (input) => input.replace(/[<>"'`]/g, "").trim();

  // verify email input is valid (uses regex)
  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  };

  // added delay for rate limiting after X amount of failed login attempts
  const delay = (ms) => new Promise((res) => setTimeout(res, ms));

  // handles login process
  const handleLogin = async (username, password) => {
  setError(null);
  // validates email prior to proceeding
  if (!validateEmail(username)) {
    setError("Please enter a valid email address.");
    return;
  }
  // delay rate limit threshold
  if (attempts >= 3) {
    await delay(3000);
  }

  setIsSubmitting(true);

  try {
    // makes the POST request to the backend login API
    const res = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // send SANITIZED email and password
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    // checks for success (200 status code)
    if (res.ok) {
      localStorage.setItem("token", data.access_token);
      // Dashboard redirect
      navigate("/dashboard");
    } else {
      // hanldes login failures and increments
      setAttempts((prev) => prev + 1);
      setError(data.detail || "Login failed.");
    }
  } catch (err) {
    console.error(err);
    // Show generic failure to user (this helps with security as it does not give direct logical information away)
    setError("Server error. Please try again later.");
  } finally {
    setIsSubmitting(false);
  }
};

  // function triggers when the login form is submitted
  const handleSubmit = async (e) => {
  e.preventDefault();
  setError(null);

  const sanitizedEmail = sanitizeInput(email);
  const sanitizedPassword = sanitizeInput(password);

  await handleLogin(sanitizedEmail, sanitizedPassword);
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
      <p className="signup-link">
        Don't have an account? <Link to="/signup">Sign up here</Link>
      </p>
    </div>
  );
}

export default LoginPage;
