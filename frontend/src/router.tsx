import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import App from './App';
import RequireAuth from './infrastructure/auth/RequireAuth';
import AvatarCreatorPage from './pages/AvatarCreatorPage';
import AvatarGalleryPage from './pages/AvatarGalleryPage';
import ChampionshipPage from './pages/ChampionshipPage';
import ChildProfileSelectPage from './pages/ChildProfileSelectPage';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ParentDashboardPage from './pages/ParentDashboardPage';
import RaceScreenPage from './pages/RaceScreenPage';
import RaceSetupPage from './pages/RaceSetupPage';
import RegisterPage from './pages/RegisterPage';
import ResultsScreenPage from './pages/ResultsScreenPage';
import SettingsPage from './pages/SettingsPage';
import StatisticsPage from './pages/StatisticsPage';

export const routeConfig: RouteObject[] = [
  {
    element: <App />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
      {
        element: <RequireAuth />,
        children: [
          { path: '/child-profiles', element: <ChildProfileSelectPage /> },
          { index: true, element: <HomePage /> },
          { path: '/avatars', element: <AvatarGalleryPage /> },
          { path: '/avatars/new', element: <AvatarCreatorPage /> },
          { path: '/race/setup', element: <RaceSetupPage /> },
          { path: '/race/:id', element: <RaceScreenPage /> },
          { path: '/race/:id/results', element: <ResultsScreenPage /> },
          { path: '/statistics', element: <StatisticsPage /> },
          { path: '/settings', element: <SettingsPage /> },
          { path: '/parent', element: <ParentDashboardPage /> },
          { path: '/championship/:id', element: <ChampionshipPage /> },
        ],
      },
    ],
  },
];

export const router = createBrowserRouter(routeConfig);
