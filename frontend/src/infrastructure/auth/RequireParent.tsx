import { Navigate, Outlet } from 'react-router-dom';
import { LoadingSpinner } from '../../shared/components/LoadingSpinner';
import { useAuth } from './AuthContext';

export default function RequireParent() {
  const { account, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner />;
  if (account?.role !== 'parent') return <Navigate to="/" replace />;
  return <Outlet />;
}
