import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Download, Eye } from 'lucide-react';

const ImageGallery = ({ gameId, images, prompts, currentStep, currentPlayer, totalPlayers }) => {
  const [selectedImage, setSelectedImage] = useState(null);

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
      return images.map((imagePath, index) => ({
        path: imagePath,
        index: index,
        label: index === 0 ? 'Original Image' : `Player ${index}'s Modification`,
        prompt: index > 0 ? prompts[index - 1]?.prompt : null
      }));
    } else if (currentStep === 'playing') {
      // During gameplay, only show the image the current player needs to modify
      const imagesToShow = [];
      
      // Always show the original image
      imagesToShow.push({
        path: images[0],
        index: 0,
        label: 'Original Image',
        prompt: null
      });
      
      // Show the image the current player needs to modify (the previous player's image)
      if (images.length > 1) {
        const currentImageIndex = images.length - 1;
        imagesToShow.push({
          path: images[currentImageIndex],
          index: currentImageIndex,
          label: `Player ${currentPlayer - 1}'s Image (Your Turn)`,
          prompt: prompts[currentImageIndex - 1]?.prompt
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
            You can see the original image and the image you need to modify (Player {currentPlayer - 1}'s creation).
            {currentPlayer < totalPlayers && ` Player ${currentPlayer + 1} will only see your modification, not the full chain.`}
          </p>
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
                className="w-full h-48 object-cover cursor-pointer transition-transform duration-200 group-hover:scale-105"
                onClick={() => handleImageClick(imageData.index)}
              />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                <Eye className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              </div>
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
              
              {imageData.prompt && (
                <div className="bg-white p-3 rounded border">
                  <p className="text-sm text-gray-600 mb-1">Prompt:</p>
                  <p className="text-gray-800 font-medium">"{imageData.prompt}"</p>
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
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
            >
              <span className="text-2xl">×</span>
            </button>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSelectedImage(Math.max(0, selectedImage - 1))}
                disabled={selectedImage === 0}
                className="text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-8 w-8" />
              </button>
              
              <img
                src={getImageUrl(selectedImage)}
                alt={`Image ${selectedImage + 1}`}
                className="max-w-full max-h-[80vh] object-contain"
              />
              
              <button
                onClick={() => setSelectedImage(Math.min(images.length - 1, selectedImage + 1))}
                disabled={selectedImage === images.length - 1}
                className="text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-8 w-8" />
              </button>
            </div>
            
            <div className="text-center mt-4 text-white">
              <p className="text-lg font-medium">
                {selectedImage === 0 ? 'Original Image' : `Player ${selectedImage}'s Modification`}
              </p>
              {selectedImage > 0 && prompts[selectedImage - 1] && (
                <p className="text-sm opacity-90 mt-1">"{prompts[selectedImage - 1].prompt}"</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGallery; 