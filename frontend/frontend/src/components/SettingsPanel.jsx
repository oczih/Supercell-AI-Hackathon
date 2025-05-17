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
    <div className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Load Analysis Data</h2>
      <p className="mb-6 text-gray-600">
        Enter the paths to your Reddit posts, comments, and sentiment analysis files.
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium mb-1">Posts File Path</label>
          <input
            type="text"
            value={postsFile}
            onChange={(e) => setPostsFile(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="e.g., data/posts.json"
            required
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Comments File Path</label>
          <input
            type="text"
            value={commentsFile}
            onChange={(e) => setCommentsFile(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="e.g., data/comments.json"
            required
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Sentiment Analysis File Path</label>
          <input
            type="text"
            value={analysisFile}
            onChange={(e) => setAnalysisFile(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="e.g., data/sentiment.json"
            required
          />
        </div>

        <button
          type="submit"
          className={`w-full px-4 py-2 text-white font-semibold rounded-md ${
            loading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Load Data'}
        </button>
      </form>
    </div>
  );
}

export default SettingsPanel;
