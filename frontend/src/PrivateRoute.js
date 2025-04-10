import { Navigate } from "react-router-dom";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token"); // Match your login save key

  return token ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
