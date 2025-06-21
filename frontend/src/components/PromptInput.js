import React, { useState } from 'react';
import { Send, Sparkles, CheckCircle, Users } from 'lucide-react';

const PromptInput = ({ value, onChange, onSubmit, currentPlayer, totalPlayers, prompts }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!value.trim() || isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit();
      setIsSubmitted(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextPlayer = () => {
    setIsSubmitted(false);
    onChange('');
  };

  // Show success message after submission
  if (isSubmitted) {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-green-800 mb-2">
            Prompt Submitted Successfully!
          </h3>
          <p className="text-green-700 mb-4">
            Your image modification is being processed by AI...
          </p>
          
          {currentPlayer < totalPlayers ? (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-center space-x-2 mb-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  <span className="font-semibold text-blue-800">
                    Next: Player {currentPlayer + 1}
                  </span>
                </div>
                <p className="text-blue-700 text-sm">
                  Pass the computer to Player {currentPlayer + 1} when the new image appears
                </p>
              </div>
              
              <button
                onClick={handleNextPlayer}
                className="btn-primary flex items-center justify-center w-full"
              >
                <Users className="h-4 w-4 mr-2" />
                Ready for Next Player
              </button>
            </div>
          ) : (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-purple-700 font-medium">
                🎉 You're the final player! The complete image chain will be revealed soon.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Player Info */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 p-4 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">
              Player {currentPlayer} of {totalPlayers}
            </h3>
            <p className="text-gray-600 text-sm">
              {currentPlayer === 1 
                ? prompts[0]?.player === 'AI' 
                  ? "You see an AI-generated image. What prompt do you think the AI used?"
                  : "You're modifying the original image"
                : `You see Player ${currentPlayer - 1}'s image, but AI works from the original`
              }
            </p>
          </div>
          <div className="bg-primary-100 rounded-full p-2">
            <Sparkles className="h-5 w-5 text-primary-600" />
          </div>
        </div>
      </div>

      {/* Prompt Input */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Prompt
          </label>
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Describe how you want to modify the image..."
            className="input-field h-24 resize-none"
            disabled={isSubmitting}
          />
        </div>
        
        <button
          type="submit"
          disabled={!value.trim() || isSubmitting}
          className="btn-primary w-full flex items-center justify-center py-3 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              Submit Prompt
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default PromptInput; 