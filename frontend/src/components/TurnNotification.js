import React, { useState, useEffect } from 'react';
import { Users, Bell, ArrowRight, Clock } from 'lucide-react';

const TurnNotification = ({ currentPlayer, totalPlayers, onContinue }) => {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleContinue = () => {
    setIsVisible(false);
    onContinue();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center animate-fade-in">
        {/* Icon */}
        <div className="bg-yellow-100 rounded-full p-4 w-20 h-20 mx-auto mb-6 flex items-center justify-center">
          <Bell className="h-10 w-10 text-yellow-600 animate-pulse" />
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Player {currentPlayer}'s Turn!
        </h2>

        {/* Message */}
        <div className="space-y-4 mb-8">
          <p className="text-gray-600 text-lg">
            It's your turn to modify the image!
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span className="font-semibold text-blue-800">Player {currentPlayer} of {totalPlayers}</span>
            </div>
            <p className="text-blue-700 text-sm">
              {currentPlayer === 1 
                ? "You'll see an AI-generated image and need to guess its prompt"
                : `You'll see Player ${currentPlayer - 1}'s creation, but AI works from the original image`
              }
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-center justify-center space-x-2">
              <Clock className="h-4 w-4 text-yellow-600" />
              <span className="text-yellow-800 text-sm font-medium">
                Time elapsed: {formatTime(timeElapsed)}
              </span>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-gray-50 rounded-lg p-4 mb-8">
          <h3 className="font-semibold text-gray-800 mb-2">Instructions:</h3>
          <ul className="text-sm text-gray-600 space-y-1 text-left">
            <li>• Look at the image you need to modify</li>
            <li>• Write a prompt describing how to change it</li>
            <li>• Submit your prompt to see the AI transformation</li>
            <li>• Pass the computer to the next player</li>
          </ul>
        </div>

        {/* Continue Button */}
        <button
          onClick={handleContinue}
          className="btn-primary w-full flex items-center justify-center text-lg py-4"
        >
          I'm Ready to Play!
          <ArrowRight className="ml-2 h-5 w-5" />
        </button>

        {/* Skip Option */}
        <button
          onClick={handleContinue}
          className="text-gray-500 hover:text-gray-700 mt-4 text-sm underline"
        >
          Skip this notification in the future
        </button>
      </div>
    </div>
  );
};

export default TurnNotification; 