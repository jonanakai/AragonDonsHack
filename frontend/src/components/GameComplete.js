import React, { useState, useEffect } from 'react';
import { Sparkles, Eye, Users, Trophy, Star, Zap, Heart, Crown, ChevronLeft, ChevronRight, Play, Pause, Target } from 'lucide-react';

const GameComplete = ({ gameState, onResetGame, onNewGame }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isRevealing, setIsRevealing] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [showAllPrompts, setShowAllPrompts] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const totalSlides = gameState.images.length;

  useEffect(() => {
    // Start the reveal sequence
    const startReveal = () => {
      setTimeout(() => {
        setIsRevealing(false);
        setShowAllPrompts(true);
        setShowConfetti(true);
      }, 2000);
    };

    startReveal();
  }, []);

  // Auto-analyze results when game is complete
  useEffect(() => {
    if (gameState.status === 'completed' && !analysisResults && !isAnalyzing) {
      analyzeGameResults();
    }
  }, [gameState.status, analysisResults, isAnalyzing]);

  const analyzeGameResults = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`/api/game/${gameState.gameId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const results = await response.json();
        setAnalysisResults(results);
      } else {
        console.error('Failed to analyze game results');
      }
    } catch (error) {
      console.error('Error analyzing game results:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Auto-play functionality
  useEffect(() => {
    if (!isAutoPlaying || currentSlide >= totalSlides - 1) return;

    const timer = setTimeout(() => {
      setCurrentSlide(prev => prev + 1);
    }, 3000); // 3 seconds per slide

    return () => clearTimeout(timer);
  }, [currentSlide, isAutoPlaying, totalSlides]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (event) => {
      switch (event.key) {
        case 'ArrowRight':
        case ' ':
          event.preventDefault();
          nextSlide();
          break;
        case 'ArrowLeft':
          event.preventDefault();
          prevSlide();
          break;
        case 'Home':
          event.preventDefault();
          goToSlide(0);
          break;
        case 'End':
          event.preventDefault();
          goToSlide(totalSlides - 1);
          break;
        case 'Escape':
          event.preventDefault();
          setIsAutoPlaying(false);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentSlide, totalSlides]);

  const getImageUrl = (imageIndex) => {
    return `/api/game/${gameState.gameId}/image/${imageIndex}`;
  };

  const getRevealIcon = (index) => {
    const icons = [Sparkles, Star, Zap, Heart, Crown, Trophy];
    const IconComponent = icons[index % icons.length];
    return <IconComponent className="h-8 w-8" />;
  };

  const nextSlide = () => {
    if (currentSlide < totalSlides - 1) {
      setCurrentSlide(prev => prev + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  const goToSlide = (slideIndex) => {
    setCurrentSlide(slideIndex);
  };

  const toggleAutoPlay = () => {
    setIsAutoPlaying(!isAutoPlaying);
  };

  // Confetti component
  const Confetti = () => {
    if (!showConfetti) return null;
    
    const pieces = Array.from({ length: 50 }, (_, i) => (
      <div
        key={i}
        className="confetti-piece"
        style={{
          left: `${Math.random() * 100}%`,
          animationDelay: `${Math.random() * 2}s`,
          animationDuration: `${2 + Math.random() * 2}s`
        }}
      />
    ));

    return (
      <div className="fixed inset-0 pointer-events-none z-40">
        {pieces}
      </div>
    );
  };

  if (isRevealing) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center z-50">
        <div className="text-center">
          <div className="animate-pulse mb-8">
            <Trophy className="h-24 w-24 text-yellow-400 mx-auto mb-4 glow-gold" />
          </div>
          <h1 className="text-6xl font-bold text-white mb-4 animate-celebration-bounce animate-rainbow-text">
            GAME COMPLETE!
          </h1>
          <div className="flex justify-center space-x-4">
            <Sparkles className="h-8 w-8 text-yellow-400 animate-spin" />
            <Star className="h-8 w-8 text-yellow-400 animate-pulse" />
            <Zap className="h-8 w-8 text-yellow-400 animate-bounce" />
            <Heart className="h-8 w-8 text-yellow-400 animate-ping" />
            <Crown className="h-8 w-8 text-yellow-400 animate-spin" />
          </div>
          <p className="text-xl text-yellow-200 mt-8 animate-pulse">
            Preparing your presentation...
          </p>
        </div>
      </div>
    );
  }

  const currentImage = gameState.images[currentSlide];
  const currentPrompt = currentSlide > 0 ? gameState.prompts[currentSlide - 1] : null;
  const isAIPrompt = currentPrompt?.player === 'AI';
  const playerNumber = isAIPrompt ? 'AI' : currentSlide;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      <Confetti />
      
      <div className="min-h-screen flex flex-col">
        {/* Header */}
        <div className="text-center py-4 animate-dramatic-reveal flex-shrink-0">
          <div className="flex items-center justify-center space-x-4 mb-2">
            <Trophy className="h-8 w-8 text-yellow-500 animate-spin" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent animate-rainbow-text">
              🎉 TELEPHONE CHAIN REVEALED! 🎉
            </h1>
            <Trophy className="h-8 w-8 text-yellow-500 animate-spin" />
          </div>
          <p className="text-gray-600">
            Slide {currentSlide + 1} of {totalSlides}
          </p>
          <div className="text-xs text-gray-500 mt-1">
            Use ← → arrows, spacebar, or click to navigate • ESC to stop auto-play
          </div>
        </div>

        {/* Main Slide Content */}
        <div className="flex-1 flex items-center justify-center px-8 py-4 overflow-hidden">
          <div className="max-w-4xl w-full h-full flex items-center">
            {/* Slide Content */}
            <div className="card animate-dramatic-reveal w-full max-h-full overflow-y-auto">
              {/* Slide Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-full ${
                    currentSlide === 0 ? 'bg-green-100 text-green-600 glow-gold' :
                    isAIPrompt ? 'bg-purple-100 text-purple-600 glow-purple' :
                    'bg-blue-100 text-blue-600 glow-blue'
                  } animate-sparkle`}>
                    {currentSlide === 0 ? (
                      <Eye className="h-6 w-6" />
                    ) : (
                      getRevealIcon(currentSlide)
                    )}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">
                      {currentSlide === 0 ? 'Original Image' : 
                       isAIPrompt ? '🤖 AI-Generated Starting Point' :
                       `Player ${playerNumber}'s Creation`}
                    </h2>
                    <p className="text-gray-500 text-sm">
                      {currentSlide === 0 ? 'The starting point of our journey' :
                       isAIPrompt ? 'Random AI creativity unleashed!' :
                       `Player ${playerNumber}'s interpretation`}
                    </p>
                  </div>
                </div>
                
                {currentSlide > 0 && (
                  <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium animate-bounce">
                    #{currentSlide}
                  </div>
                )}
              </div>

              {/* Image */}
              <div className="relative group mb-4">
                <img
                  src={getImageUrl(currentSlide)}
                  alt={`Image ${currentSlide + 1}`}
                  className="w-full h-80 object-contain bg-white rounded-lg shadow-lg border-2 border-gray-200 group-hover:border-blue-300 transition-all duration-300 hover:scale-105"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 rounded-lg flex items-center justify-center">
                  <Eye className="h-12 w-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
              </div>

              {/* Prompt Reveal */}
              {currentSlide > 0 && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-4 animate-dramatic-reveal">
                  <div className="flex items-center space-x-2 mb-2">
                    <Sparkles className="h-5 w-5 text-purple-600 animate-spin" />
                    <h3 className="font-semibold text-purple-800">
                      {isAIPrompt ? '🤖 AI Prompt' : `Player ${playerNumber}'s Prompt`}
                    </h3>
                  </div>
                  <div className="bg-white p-4 rounded border-l-4 border-purple-400 hover:shadow-lg transition-shadow duration-300">
                    <p className="text-lg font-medium text-gray-800 italic">
                      "{currentPrompt?.prompt}"
                    </p>
                  </div>
                  {isAIPrompt && (
                    <p className="text-sm text-purple-600 mt-2">
                      🎲 This was randomly generated by AI to start the game!
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Navigation Controls - Always Visible */}
        <div className="py-4 px-8 flex-shrink-0 bg-white bg-opacity-90 backdrop-blur-sm border-t border-gray-200">
          <div className="max-w-4xl mx-auto">
            {/* Progress Bar */}
            <div className="mb-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((currentSlide + 1) / totalSlides) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={prevSlide}
                  disabled={currentSlide === 0}
                  className="btn-secondary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </button>
                
                <button
                  onClick={toggleAutoPlay}
                  className={`flex items-center px-4 py-2 rounded-lg transition-colors duration-200 ${
                    isAutoPlaying 
                      ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {isAutoPlaying ? (
                    <>
                      <Pause className="h-4 w-4 mr-1" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-1" />
                      Auto Play
                    </>
                  )}
                </button>
              </div>

              <div className="flex items-center space-x-2">
                {Array.from({ length: totalSlides }, (_, index) => (
                  <button
                    key={index}
                    onClick={() => goToSlide(index)}
                    className={`w-3 h-3 rounded-full transition-all duration-200 ${
                      index === currentSlide 
                        ? 'bg-purple-600 scale-125' 
                        : 'bg-gray-300 hover:bg-gray-400'
                    }`}
                  />
                ))}
              </div>

              <button
                onClick={nextSlide}
                disabled={currentSlide === totalSlides - 1}
                className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </button>
            </div>
          </div>
        </div>

        {/* Final Actions and Analysis (only on last slide) */}
        {currentSlide === totalSlides - 1 && (
          <div className="py-6 px-8 bg-gradient-to-r from-yellow-50 to-orange-50 border-t border-yellow-200">
            <div className="max-w-4xl mx-auto">
              <div className="bg-gradient-to-r from-yellow-100 to-orange-100 border-2 border-yellow-300 rounded-lg p-6 text-center animate-dramatic-reveal">
                <div className="flex justify-center space-x-4 mb-4">
                  <Trophy className="h-6 w-6 text-yellow-600 animate-bounce" />
                  <Star className="h-6 w-6 text-yellow-600 animate-spin" />
                  <Crown className="h-6 w-6 text-yellow-600 animate-pulse" />
                </div>
                <h3 className="text-xl font-bold text-yellow-800 mb-3 animate-rainbow-text">
                  🎊 Amazing Telephone Chain Complete! 🎊
                </h3>
                <p className="text-yellow-700 mb-4 text-sm">
                  Look at how creative everyone was! Each interpretation added something unique to the chain.
                </p>
                
                {/* Analysis Results */}
                {isAnalyzing && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                      <span className="text-blue-700">Analyzing results...</span>
                    </div>
                  </div>
                )}
                
                {analysisResults && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mb-6">
                    <div className="flex items-center justify-center space-x-2 mb-3">
                      <Target className="h-6 w-6 text-purple-600" />
                      <h4 className="font-semibold text-purple-800 text-lg">Final Score</h4>
                    </div>
                    <div className="text-4xl font-bold text-purple-600 mb-3">
                      {analysisResults.final_score}
                    </div>
                    <p className="text-purple-700 mb-4">
                      Based on prompt similarity, image similarity, and overall coherence
                    </p>
                    
                    {/* Score Breakdown */}
                    <div className="grid grid-cols-3 gap-3 mb-6">
                      <div className="bg-white p-3 rounded-lg shadow-sm">
                        <div className="font-semibold text-blue-600 text-sm">Prompt Similarity</div>
                        <div className="text-gray-800 text-lg font-bold">
                          {((analysisResults.prompt_semantic_scores.reduce((a, b) => a + b, 0) / analysisResults.prompt_semantic_scores.length + 1) / 2 * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="bg-white p-3 rounded-lg shadow-sm">
                        <div className="font-semibold text-green-600 text-sm">Image Similarity</div>
                        <div className="text-gray-800 text-lg font-bold">
                          {((analysisResults.image_similarity_scores.reduce((a, b) => a + b, 0) / analysisResults.image_similarity_scores.length + 1) / 2 * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="bg-white p-3 rounded-lg shadow-sm">
                        <div className="font-semibold text-red-600 text-sm">Text Coherence</div>
                        <div className="text-gray-800 text-lg font-bold">
                          {(analysisResults.prompt_levenshtein_scores.reduce((a, b) => a + b, 0) / analysisResults.prompt_levenshtein_scores.length * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-4 justify-center">
                  <button
                    onClick={onResetGame}
                    className="btn-secondary flex items-center px-6 py-3 text-base hover:scale-105 transition-transform duration-200"
                  >
                    <Sparkles className="h-5 w-5 mr-2 animate-spin" />
                    Play Again
                  </button>
                  <button
                    onClick={onNewGame}
                    className="btn-primary flex items-center px-6 py-3 text-base hover:scale-105 transition-transform duration-200"
                  >
                    <Trophy className="h-5 w-5 mr-2 animate-bounce" />
                    New Game
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GameComplete; 