import React from 'react';

function WordCloud({ imageUrl }) {
  if (!imageUrl) {
    return (
      <div className="bg-light p-4 rounded d-flex justify-content-center align-items-center" style={{ height: '16rem' }}>
        <p className="text-muted mb-0">Word cloud not available</p>
      </div>
    );
  }

  return (
    <div className="bg-light p-4 rounded">
      <h2 className="h5 fw-semibold mb-4">Word Cloud</h2>
      <div className="d-flex justify-content-center">
        <img 
          src={imageUrl} 
          alt="Word Cloud" 
          className="img-fluid" 
          style={{ maxHeight: '16rem', objectFit: 'contain' }}
        />
      </div>
    </div>
  );
}

export default WordCloud;
