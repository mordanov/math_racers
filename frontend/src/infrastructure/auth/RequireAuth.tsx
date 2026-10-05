import { Navigate, Outlet } from 'react-router-dom';
import { LoadingSpinner } from '../../shared/components/LoadingSpinner';
import { useAuth } from './AuthContext';

export default function RequireAuth() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner message="Loading…" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Outlet />;
}
