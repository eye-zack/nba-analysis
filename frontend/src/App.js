//import logo from './logo.svg';
//import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./LoginPage";
import DashboardPage from "./DashboardPage";
import SignupPage from "./SignupPage";
import PrivateRoute from './PrivateRoute';
import User from './UserPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route path="/user" 
        element={
          <PrivateRoute>
            <User />
          </PrivateRoute>
        } 
        />
        {/* Catch-all route for undefined paths */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;