import React, { useState } from 'react';

function SettingsPanel({ onLoadData, loading }) {
  const [postsFile, setPostsFile] = useState('');
  const [commentsFile, setCommentsFile] = useState('');
  const [analysisFile, setAnalysisFile] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!postsFile || !commentsFile || !analysisFile) return;
    onLoadData(postsFile, commentsFile, analysisFile);
  };

  return (
    <div className="bg-white p-4 rounded shadow-sm mx-auto" style={{ maxWidth: '600px' }}>
      <h2 className="h4 mb-3">Load Analysis Data</h2>
      <p className="text-muted mb-4">
        Enter the paths to your Reddit posts, comments, and sentiment analysis files.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Posts File Path</label>
          <input
            type="text"
            value={postsFile}
            onChange={(e) => setPostsFile(e.target.value)}
            className="form-control"
            placeholder="e.g., data/posts.json"
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Comments File Path</label>
          <input
            type="text"
            value={commentsFile}
            onChange={(e) => setCommentsFile(e.target.value)}
            className="form-control"
            placeholder="e.g., data/comments.json"
            required
          />
        </div>

        <div className="mb-4">
          <label className="form-label">Sentiment Analysis File Path</label>
          <input
            type="text"
            value={analysisFile}
            onChange={(e) => setAnalysisFile(e.target.value)}
            className="form-control"
            placeholder="e.g., data/sentiment.json"
            required
          />
        </div>

        <button
          type="submit"
          className={`btn w-100 fw-semibold ${loading ? 'btn-primary disabled' : 'btn-primary'}`}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Load Data'}
        </button>
      </form>
    </div>
  );
}

export default SettingsPanel;
