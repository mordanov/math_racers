import { Outlet } from 'react-router-dom';
import OfflineResultSync from './infrastructure/offline/OfflineResultSync';

export default function App() {
  return (
    <>
      <OfflineResultSync />
      <Outlet />
    </>
  );
}
