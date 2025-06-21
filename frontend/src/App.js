import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import HomePage from './components/HomePage';
import GamePage from './components/GamePage';
import LoadingSpinner from './components/LoadingSpinner';

// Configure axios base URL
axios.defaults.baseURL = 'http://localhost:5000';

function App() {
  const [gameId, setGameId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createGame = async (numPlayers) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/game/create', { numPlayers });
      setGameId(response.data.gameId);
      setGameState(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const uploadImage = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('image', file);
      
      const response = await axios.post(`/api/game/${gameId}/upload-image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setGameState(prev => ({ ...prev, ...response.data }));
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload image');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const submitPrompt = async (prompt) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/game/${gameId}/submit-prompt`, { prompt });
      setGameState(prev => ({ ...prev, ...response.data }));
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit prompt');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetGame = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/game/${gameId}/reset`);
      setGameState(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reset game');
    } finally {
      setLoading(false);
    }
  };

  const fetchGameStatus = async () => {
    if (!gameId) return;
    
    try {
      const response = await axios.get(`/api/game/${gameId}/status`);
      setGameState(response.data);
    } catch (err) {
      console.error('Failed to fetch game status:', err);
    }
  };

  // Poll for game status updates
  useEffect(() => {
    if (!gameId) return;
    
    const interval = setInterval(fetchGameStatus, 2000);
    return () => clearInterval(interval);
  }, [gameId]);

  const clearError = () => setError(null);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {error && (
          <div className="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50">
            <span className="block sm:inline">{error}</span>
            <button 
              onClick={clearError}
              className="ml-2 text-red-700 hover:text-red-900"
            >
              ×
            </button>
          </div>
        )}
        
        <Routes>
          <Route 
            path="/" 
            element={
              gameId ? (
                <Navigate to="/game" replace />
              ) : (
                <HomePage onCreateGame={createGame} />
              )
            } 
          />
          <Route 
            path="/game" 
            element={
              gameId ? (
                <GamePage 
                  gameId={gameId}
                  gameState={gameState}
                  onUploadImage={uploadImage}
                  onSubmitPrompt={submitPrompt}
                  onResetGame={resetGame}
                  onNewGame={() => {
                    setGameId(null);
                    setGameState(null);
                  }}
                />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 