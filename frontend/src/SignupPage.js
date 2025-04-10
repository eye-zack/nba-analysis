import React, { useState } from "react";
import "./SignupPage.css";
import { useNavigate, Link } from "react-router-dom";

function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  // sanitization to remove characters
  const sanitizeInput = (input) => input.replace(/[<>"'`]/g, "").trim();

  // validates the email is formated correctly
  const validateEmail = (email) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email.toLowerCase());
  };

  // verifies the password meets the requirements
  const validatePassword = (pwd) => {
    const pattern =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return pattern.test(pwd);
  };

  // handle the actual signup process be sending POST to the backend
  const handleSignup = async (username, password) => {
    try {
      // sends POST with SANITIZED credentials
      const res = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      // checks for success (200 status code)
      if (res.ok) {
        setSuccess("Signup successful. Redirecting...");
        // auto redirect to login after 1.5 seconds
        setTimeout(() => navigate("/login"), 1500);
      } else {
        setError(data.detail || "Signup failed. Try again.");
      }
    } catch (err) {
      console.error(err);
      // generic error message
      setError("Server error. Please try again later.");
    }
  };

  // submission form handling
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const sanitizedEmail = sanitizeInput(email);
    const sanitizedPassword = sanitizeInput(password);
    const sanitizedConfirm = sanitizeInput(confirmPassword);

    if (!validateEmail(sanitizedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    // validates password meets formated requirements
    if (!validatePassword(sanitizedPassword)) {
      setError(
        "Password must be at least 8 characters and include uppercase, lowercase, number, and special character."
      );
      return;
    }

    // checks if password and confirm password match
    if (sanitizedPassword !== sanitizedConfirm) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    await handleSignup(sanitizedEmail, sanitizedPassword);
    setIsSubmitting(false);
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit} autoComplete="off">
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <div className="password-wrapper">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            type="button"
            className="toggle-password"
            title="Toggle password visibility"
            onClick={() => setShowPassword((prev) => !prev)}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        <input
          type={showPassword ? "text" : "password"}
          placeholder="Confirm Password"
          required
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating Account..." : "Register"}
        </button>
      </form>

      <p className="login-link">
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </div>
  );
}

export default SignupPage;
