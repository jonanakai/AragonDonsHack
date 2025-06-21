import React from 'react';
import { Users, Clock, CheckCircle, Play } from 'lucide-react';

const GameStatus = ({ gameState }) => {
  if (!gameState) {
    return (
      <div className="bg-gray-100 rounded-lg p-4 mb-6">
        <div className="animate-pulse flex space-x-4">
          <div className="rounded-full bg-gray-300 h-10 w-10"></div>
          <div className="flex-1 space-y-2 py-1">
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'waiting_for_image':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'ready':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'waiting_for_image':
        return <Clock className="h-4 w-4" />;
      case 'ready':
        return <Play className="h-4 w-4" />;
      case 'in_progress':
        return <Users className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'waiting_for_image':
        return 'Waiting for starting image';
      case 'ready':
        return 'Ready to start';
      case 'in_progress':
        return 'Game in progress';
      case 'completed':
        return 'Game completed';
      default:
        return 'Unknown status';
    }
  };

  const completedRounds = gameState.images ? Math.max(0, gameState.images.length - 1) : 0;
  const totalRounds = gameState.numPlayers || 0;
  const progressPercentage = totalRounds > 0 ? (completedRounds / totalRounds) * 100 : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="grid md:grid-cols-3 gap-6">
        {/* Game Status */}
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full ${getStatusColor(gameState.status)}`}>
            {getStatusIcon(gameState.status)}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Status</p>
            <p className="text-lg font-semibold text-gray-800">
              {getStatusText(gameState.status)}
            </p>
          </div>
        </div>

        {/* Player Progress */}
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-full bg-primary-100 text-primary-600">
            <Users className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Current Player</p>
            <p className="text-lg font-semibold text-gray-800">
              {gameState.currentPlayer} of {gameState.numPlayers}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-full bg-green-100 text-green-600">
            <CheckCircle className="h-4 w-4" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">Progress</p>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-600">
                {completedRounds}/{totalRounds}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      {gameState.status === 'in_progress' && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Next:</span> Player {gameState.currentPlayer} should enter their prompt to modify the current image.
          </p>
        </div>
      )}

      {gameState.status === 'completed' && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Complete!</span> All players have taken their turns. Check out the final image chain below.
          </p>
        </div>
      )}
    </div>
  );
};

export default GameStatus; 