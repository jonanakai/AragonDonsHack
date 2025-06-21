import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Send, RotateCcw, Home, Image as ImageIcon, Users, CheckCircle } from 'lucide-react';
import ImageUpload from './ImageUpload';
import PromptInput from './PromptInput';
import ImageGallery from './ImageGallery';
import GameStatus from './GameStatus';
import TurnNotification from './TurnNotification';

const GamePage = ({ 
  gameId, 
  gameState, 
  onUploadImage, 
  onSubmitPrompt, 
  onResetGame, 
  onNewGame 
}) => {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [showTurnNotification, setShowTurnNotification] = useState(false);
  const [lastPlayerTurn, setLastPlayerTurn] = useState(null);

  // Show turn notification when player changes
  React.useEffect(() => {
    if (gameState?.currentPlayer && gameState.currentPlayer !== lastPlayerTurn) {
      setLastPlayerTurn(gameState.currentPlayer);
      if (gameState.status === 'in_progress' || gameState.status === 'ready') {
        setShowTurnNotification(true);
      }
    }
  }, [gameState?.currentPlayer, gameState?.status, lastPlayerTurn]);

  const handleImageUpload = async (file) => {
    try {
      await onUploadImage(file);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handlePromptSubmit = async () => {
    if (!currentPrompt.trim()) return;
    
    try {
      await onSubmitPrompt(currentPrompt);
      setCurrentPrompt('');
    } catch (error) {
      console.error('Prompt submission failed:', error);
    }
  };

  const handleTurnNotificationContinue = () => {
    setShowTurnNotification(false);
  };

  const getCurrentStep = () => {
    if (!gameState) return 'loading';
    if (gameState.status === 'waiting_for_image') return 'upload';
    if (gameState.status === 'completed') return 'complete';
    return 'playing';
  };

  const currentStep = getCurrentStep();

  return (
    <div className="min-h-screen p-4">
      {/* Turn Notification */}
      {showTurnNotification && gameState && (
        <TurnNotification
          currentPlayer={gameState.currentPlayer}
          totalPlayers={gameState.numPlayers}
          onContinue={handleTurnNotificationContinue}
        />
      )}

      {/* Header */}
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold text-gray-800">AI Image Telephone</h1>
            <div className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
              Game ID: {gameId?.slice(0, 8)}...
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={onResetGame}
              className="btn-secondary flex items-center"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </button>
            <button
              onClick={onNewGame}
              className="btn-primary flex items-center"
            >
              <Home className="h-4 w-4 mr-2" />
              New Game
            </button>
          </div>
        </div>

        {/* Game Status */}
        <GameStatus gameState={gameState} />

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Game Controls */}
          <div className="space-y-6">
            {currentStep === 'upload' && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <ImageIcon className="h-5 w-5 mr-2" />
                  Upload Starting Image
                </h2>
                <ImageUpload onUpload={handleImageUpload} />
              </div>
            )}

            {currentStep === 'playing' && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <Users className="h-5 w-5 mr-2" />
                  Player {gameState?.currentPlayer}'s Turn
                </h2>
                <PromptInput
                  value={currentPrompt}
                  onChange={setCurrentPrompt}
                  onSubmit={handlePromptSubmit}
                  currentPlayer={gameState?.currentPlayer}
                  totalPlayers={gameState?.numPlayers}
                  prompts={gameState?.prompts}
                />
              </div>
            )}

            {currentStep === 'complete' && (
              <div className="card">
                <div className="text-center">
                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                    Game Complete!
                  </h2>
                  <p className="text-gray-600 mb-4">
                    All players have taken their turns. Check out the image chain below!
                  </p>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-purple-800 mb-2">🎉 Reveal Time!</h3>
                    <p className="text-purple-700 text-sm">
                      All prompts are now visible! See how each player interpreted the previous modifications.
                    </p>
                  </div>
                  <div className="flex space-x-3 justify-center">
                    <button
                      onClick={onResetGame}
                      className="btn-secondary flex items-center"
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Play Again
                    </button>
                    <button
                      onClick={onNewGame}
                      className="btn-primary flex items-center"
                    >
                      <Home className="h-4 w-4 mr-2" />
                      New Game
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Image Gallery */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <ImageIcon className="h-5 w-5 mr-2" />
              Image Chain
            </h2>
            <ImageGallery 
              gameId={gameId}
              images={gameState?.images || []}
              prompts={gameState?.prompts || []}
              currentStep={currentStep}
              currentPlayer={gameState?.currentPlayer}
              totalPlayers={gameState?.numPlayers}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default GamePage; 