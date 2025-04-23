import React from 'react';
import { Navigate } from "react-router-dom";
import { useEffect, useState } from 'react';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token"); // Match your login save key
  const [userData, setUserData ] = useState(null);

  useEffect(() => {
    if (token) {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        setUserData(JSON.parse(storedUser));
      }
    }
  }, [token]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // clone children and pass user data as properties
  return React.cloneElement(children, {
    favoriteTeam: userData?.favorite_team || "Atlanta Hawks"
  });
};

export default PrivateRoute;
