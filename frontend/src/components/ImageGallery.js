import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Download, Eye } from 'lucide-react';

const ImageGallery = ({ gameId, images, prompts, currentStep, currentPlayer, totalPlayers }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  // Add keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (selectedImage === null) return;
      
      switch (event.key) {
        case 'Escape':
          setSelectedImage(null);
          break;
        case 'ArrowLeft':
          setSelectedImage(prev => Math.max(0, prev - 1));
          break;
        case 'ArrowRight':
          setSelectedImage(prev => Math.min(images.length - 1, prev + 1));
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedImage, images.length]);

  if (!images || images.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-gray-100 rounded-lg p-8">
          <p className="text-gray-500">No images yet. Upload a starting image to begin!</p>
        </div>
      </div>
    );
  }

  const getImageUrl = (imageIndex) => {
    return `/api/game/${gameId}/image/${imageIndex}`;
  };

  const handleImageClick = (imageIndex) => {
    setSelectedImage(imageIndex);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const downloadImage = async (imageIndex) => {
    try {
      const response = await fetch(getImageUrl(imageIndex));
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `image-${imageIndex + 1}.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download image:', error);
    }
  };

  // Determine which images to show based on game state
  const getVisibleImages = () => {
    if (currentStep === 'upload' || currentStep === 'complete') {
      // Show all images in upload mode or when game is complete
      return images.map((imagePath, index) => {
        let label = 'Original Image';
        if (index > 0) {
          if (index === 1 && prompts[0]?.player === 'AI') {
            label = 'AI-Generated Starting Image';
          } else {
            const playerOffset = prompts[0]?.player === 'AI' ? 1 : 0;
            label = `Player ${index - playerOffset}'s Modification`;
          }
        }
        
        return {
          path: imagePath,
          index: index,
          label: label,
          prompt: index > 0 ? prompts[index - 1]?.prompt : null,
          isAI: index === 1 && prompts[0]?.player === 'AI'
        };
      });
    } else if (currentStep === 'playing') {
      // During gameplay, show the images the current player needs to see
      const imagesToShow = [];
      
      // Always show the original image
      imagesToShow.push({
        path: images[0],
        index: 0,
        label: 'Original Image',
        prompt: null,
        isAI: false
      });
      
      // Show the image the current player needs to see
      if (images.length > 1) {
        const currentImageIndex = images.length - 1;
        const isAIImage = currentImageIndex === 1 && prompts[0]?.player === 'AI';
        const playerLabel = isAIImage ? 'AI-Generated Image' : `Player ${currentPlayer - 1}'s Image (Your Turn)`;
        
        imagesToShow.push({
          path: images[currentImageIndex],
          index: currentImageIndex,
          label: playerLabel,
          prompt: prompts[currentImageIndex - 1]?.prompt,
          isAI: isAIImage
        });
      }
      
      return imagesToShow;
    }
    
    return [];
  };

  const visibleImages = getVisibleImages();

  return (
    <div className="space-y-6">
      {/* Game State Info */}
      {currentStep === 'playing' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">Your View</h3>
          <p className="text-blue-700 text-sm">
            You can see the original image and Player {currentPlayer - 1}'s creation.
            <br />
            <strong>Note:</strong> The AI will modify the <em>original image</em> based on your prompt, not Player {currentPlayer - 1}'s image.
            {currentPlayer < totalPlayers && ` Player ${currentPlayer + 1} will only see your modification, not the full chain.`}
          </p>
        </div>
      )}

      {/* Special guessing section during gameplay */}
      {currentStep === 'playing' && images.length > 1 && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-yellow-500 rounded-full p-2">
              <Eye className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-yellow-800">🔍 Study This Image</h3>
              <p className="text-yellow-700 text-sm">
                Look carefully at Player {currentPlayer - 1}'s creation below. What prompt do you think they used?
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Image Chain */}
      <div className="space-y-4">
        {visibleImages.map((imageData) => (
          <div key={imageData.index} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Image */}
            <div className="relative group">
              <img
                src={getImageUrl(imageData.index)}
                alt={imageData.label}
                className="w-full h-96 object-contain bg-gray-50 cursor-pointer transition-transform duration-200 group-hover:scale-105"
                onClick={() => handleImageClick(imageData.index)}
              />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                <Eye className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              </div>
              
              {/* Special indicator for the image to guess */}
              {currentStep === 'playing' && imageData.index === images.length - 1 && imageData.index > 0 && (
                <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
                  {imageData.isAI ? '🤖 AI Generated' : '🔍 Guess this image'}
                </div>
              )}
            </div>
            
            {/* Image Info */}
            <div className="p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-800">
                  {imageData.label}
                </h3>
                <button
                  onClick={() => downloadImage(imageData.index)}
                  className="text-gray-500 hover:text-gray-700 transition-colors duration-200"
                  title="Download image"
                >
                  <Download className="h-4 w-4" />
                </button>
              </div>
              
              {imageData.prompt && currentStep === 'complete' && (
                <div className="bg-white p-3 rounded border">
                  <p className="text-sm text-gray-600 mb-1">Prompt:</p>
                  <p className="text-gray-800 font-medium">"{imageData.prompt}"</p>
                </div>
              )}
              
              {imageData.prompt && currentStep !== 'complete' && (
                <div className="bg-gray-100 p-3 rounded border">
                  <p className="text-sm text-gray-500 mb-1">Prompt:</p>
                  <p className="text-gray-600 font-medium">🤐 Hidden until game ends</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Progress Indicator */}
      {currentStep === 'playing' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-800">Game Progress</span>
            <span className="text-sm text-blue-600">
              Player {currentPlayer} of {totalPlayers}
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentPlayer / totalPlayers) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Image Modal */}
      {selectedImage !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Close button */}
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 text-white hover:text-gray-300 z-20 bg-black bg-opacity-50 rounded-full p-2"
            >
              <span className="text-2xl">×</span>
            </button>
            
            {/* Navigation buttons */}
            <button
              onClick={() => setSelectedImage(Math.max(0, selectedImage - 1))}
              disabled={selectedImage === 0}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed z-20 bg-black bg-opacity-50 rounded-full p-2"
            >
              <ChevronLeft className="h-8 w-8" />
            </button>
            
            <button
              onClick={() => setSelectedImage(Math.min(images.length - 1, selectedImage + 1))}
              disabled={selectedImage === images.length - 1}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed z-20 bg-black bg-opacity-50 rounded-full p-2"
            >
              <ChevronRight className="h-8 w-8" />
            </button>
            
            {/* Main image */}
            <div className="max-w-full max-h-full flex flex-col items-center">
              <img
                src={getImageUrl(selectedImage)}
                alt={`Image ${selectedImage + 1}`}
                className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
                style={{ maxWidth: '90vw', maxHeight: '80vh' }}
              />
              
              {/* Image info */}
              <div className="text-center mt-4 text-white bg-black bg-opacity-50 rounded-lg p-4 max-w-md">
                <p className="text-lg font-medium">
                  {selectedImage === 0 ? 'Original Image' : `Player ${selectedImage}'s Modification`}
                </p>
                {selectedImage > 0 && prompts[selectedImage - 1] && currentStep === 'complete' && (
                  <p className="text-sm opacity-90 mt-1">"{prompts[selectedImage - 1].prompt}"</p>
                )}
                {selectedImage > 0 && prompts[selectedImage - 1] && currentStep !== 'complete' && (
                  <p className="text-sm opacity-90 mt-1">🤐 Prompt hidden until game ends</p>
                )}
                <p className="text-xs opacity-75 mt-2">
                  {selectedImage + 1} of {images.length}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGallery; 