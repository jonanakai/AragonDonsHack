import React, { useState } from 'react';
import { Users, Image, Sparkles, ArrowRight } from 'lucide-react';

const HomePage = ({ onCreateGame }) => {
  const [numPlayers, setNumPlayers] = useState(2);

  const handleCreateGame = () => {
    onCreateGame(numPlayers);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <Sparkles className="h-12 w-12 text-primary-600 mr-3" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              AI Image Telephone
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-lg mx-auto">
            Take turns modifying images with AI prompts. See how your vision transforms through the chain!
          </p>
        </div>

        {/* Game Setup Card */}
        <div className="card max-w-md mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Start a New Game</h2>
            <p className="text-gray-600">Choose how many players will participate</p>
          </div>

          {/* Player Count Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-4 text-center">
              Number of Players
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[2, 3, 4, 5, 6].map((num) => (
                <button
                  key={num}
                  onClick={() => setNumPlayers(num)}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                    numPlayers === num
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <Users className="h-6 w-6 mx-auto mb-2" />
                  <span className="font-semibold">{num}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Start Game Button */}
          <button
            onClick={handleCreateGame}
            className="btn-primary w-full flex items-center justify-center text-lg py-3"
          >
            Start Game
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>

        {/* How to Play */}
        <div className="mt-12 max-w-2xl mx-auto">
          <h3 className="text-xl font-semibold text-gray-800 mb-6 text-center">How to Play</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Image className="h-8 w-8 text-primary-600" />
              </div>
              <h4 className="font-semibold text-gray-800 mb-2">1. Upload Image</h4>
              <p className="text-gray-600 text-sm">Start with any image you'd like to transform</p>
            </div>
            <div className="text-center">
              <div className="bg-secondary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Sparkles className="h-8 w-8 text-secondary-600" />
              </div>
              <h4 className="font-semibold text-gray-800 mb-2">2. Write Prompts</h4>
              <p className="text-gray-600 text-sm">Each player describes how to modify the image</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-800 mb-2">3. See Results</h4>
              <p className="text-gray-600 text-sm">Watch how the image evolves through the chain</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 