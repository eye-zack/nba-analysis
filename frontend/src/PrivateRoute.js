import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('authToken'); // or your actual token key

  return token ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
