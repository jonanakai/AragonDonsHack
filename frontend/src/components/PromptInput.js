import React, { useState } from 'react';
import { Send, Sparkles, Lightbulb, CheckCircle, Users } from 'lucide-react';

const PromptInput = ({ value, onChange, onSubmit, currentPlayer, totalPlayers }) => {
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

  const examplePrompts = [
    "Make this a 90s cartoon style",
    "Transform into a cyberpunk scene",
    "Add a magical forest background",
    "Make it look like a watercolor painting",
    "Convert to black and white with dramatic lighting",
    "Add a futuristic city skyline",
    "Make it look like an oil painting",
    "Transform into a comic book style"
  ];

  const handleExampleClick = (example) => {
    onChange(example);
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
                ? "You're modifying the original image"
                : `You're modifying Player ${currentPlayer - 1}'s image`
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
            placeholder="Describe how you want to modify the image... (e.g., 'Make this a 90s cartoon style')"
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

      {/* Example Prompts */}
      <div>
        <div className="flex items-center mb-3">
          <Lightbulb className="h-4 w-4 text-yellow-500 mr-2" />
          <span className="text-sm font-medium text-gray-700">Example Prompts</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {examplePrompts.map((prompt, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(prompt)}
              className="text-left p-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded transition-colors duration-200"
            >
              "{prompt}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PromptInput; 