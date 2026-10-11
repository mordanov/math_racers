import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function RequireChildProfile() {
  const { activeChildId } = useAuth();
  const location = useLocation();

  if (!activeChildId) {
    return <Navigate to="/child-profiles" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
