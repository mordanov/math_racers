import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';
import AvatarGalleryPage from './pages/AvatarGalleryPage';
import AvatarCreatorPage from './pages/AvatarCreatorPage';
import RaceSetupPage from './pages/RaceSetupPage';
import RaceScreenPage from './pages/RaceScreenPage';
import ResultsScreenPage from './pages/ResultsScreenPage';
import StatisticsPage from './pages/StatisticsPage';
import SettingsPage from './pages/SettingsPage';
import ParentDashboardPage from './pages/ParentDashboardPage';
import ChampionshipPage from './pages/ChampionshipPage';

export const routeConfig: RouteObject[] = [
  {
    element: <App />,
    children: [
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
];

export const router = createBrowserRouter(routeConfig);
