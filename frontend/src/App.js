import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Composants de mise en page
import Layout from './components/Layout/Layout';

// Pages publiques
import HomePage from './pages/Home/HomePage';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import AboutPage from './pages/About/AboutPage';

// Pages protégées
import DashboardPage from './pages/Dashboard/DashboardPage';
import PhotoSearchPage from './pages/Search/PhotoSearchPage';
import NameSearchPage from './pages/Search/NameSearchPage';
import ResultsPage from './pages/Results/ResultsPage';
import ProfilePage from './pages/Profile/ProfilePage';
import HistoryPage from './pages/History/HistoryPage';

// Route protégée
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Chargement...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Routes publiques */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/about" element={<AboutPage />} />
          
          {/* Routes protégées */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          <Route path="/search/photo" element={
            <ProtectedRoute>
              <PhotoSearchPage />
            </ProtectedRoute>
          } />
          <Route path="/search/name" element={
            <ProtectedRoute>
              <NameSearchPage />
            </ProtectedRoute>
          } />
          <Route path="/results/:searchId" element={
            <ProtectedRoute>
              <ResultsPage />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          <Route path="/history" element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          } />
          
          {/* Redirection pour les routes inconnues */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
