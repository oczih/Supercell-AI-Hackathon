import React from 'react';

function WordCloud({ imageUrl }) {
  if (!imageUrl) {
    return (
      <div className="bg-gray-50 p-4 rounded-lg flex justify-center items-center h-64">
        <p className="text-gray-500">Word cloud not available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Word Cloud</h2>
      <div className="flex justify-center">
        <img 
          src={imageUrl} 
          alt="Word Cloud" 
          className="max-w-full max-h-64 object-contain"
        />
      </div>
    </div>
  );
}

export default WordCloud;