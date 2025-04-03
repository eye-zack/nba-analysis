import React, { useState } from "react";
import "./SignupPage.css";
import { useNavigate } from "react-router-dom";

function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  //email must be valid format '.com'
  const validateEmail = (email) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(String(email).toLowerCase());
  };

  const validatePassword = (pwd) => {
    // Minimum 8 characters, one uppercase, one lowercase, one number, one special char
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return pattern.test(pwd);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validateEmail(email)) {
      setError("Please enter a valid email address.")
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!validatePassword(password)) {
        setError("Password must be at least 8 characters long and include an uppercase letter, lowercase letter, a number, and a special character.");
        return;
      }

    // Simulate registration API
    console.log("Signup successful:", { email, password });
    setSuccess("Successful account creation! Redirecting to login.");

    setTimeout(() => {
        navigate("/login");
    }, 2000); 
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSignup}>
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          required
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default SignupPage;
