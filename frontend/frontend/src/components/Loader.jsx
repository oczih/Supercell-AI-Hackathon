import React from 'react';

function Loader() {
  return (
    <div className="d-flex justify-content-center align-items-center py-5">
      <div className="spinner-border text-primary me-3" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">Loading...</span>
      </div>
      <span className="text-muted">Loading data...</span>
    </div>
  );
}

export default Loader;
