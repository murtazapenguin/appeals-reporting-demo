// Claim Appeals Frontend - Force redeploy 2026-02-13
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import DenialsList from './components/DenialsList';
import SubmittedAppealsList from './components/SubmittedAppealsList';
import NewDenialWizard from './components/NewDenialWizard';
import DenialDetail from './components/DenialDetail';
import Reporting from './components/Reporting';
import PracticeSelector from './components/PracticeSelector';
import PracticeScorecard from './components/PracticeScorecard';
import PracticeComparison from './components/PracticeComparison';
import Layout from './components/Layout';

// Healthcare Claim Denial Appeal Management App
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsLoggedIn(false);
  };

  const ProtectedRoute = ({ children }) => {
    return isLoggedIn ? children : <Navigate to="/login" replace />;
  };

  return (
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isLoggedIn ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/denials"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <DenialsList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/submitted-appeals"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <SubmittedAppealsList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reporting"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <Reporting />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/practices"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <PracticeSelector />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/practices/compare"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <PracticeComparison />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/practices/:name"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <PracticeScorecard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/denials/new"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <NewDenialWizard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/denials/:id"
          element={
            <ProtectedRoute>
              <Layout onLogout={handleLogout}>
                <DenialDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            <Navigate to={isLoggedIn ? "/dashboard" : "/login"} replace />
          }
        />
      </Routes>
    </Router>
    </ThemeProvider>
  );
}

export default App;
