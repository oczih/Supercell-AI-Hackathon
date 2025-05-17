import React, { useState } from 'react';

function TopComments({ comments }) {
  const [sortBy, setSortBy] = useState('score');
  const [searchText, setSearchText] = useState('');

  const filteredComments = comments.filter(comment => 
    comment.body.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.summary.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.themes.some(theme => theme.toLowerCase().includes(searchText.toLowerCase()))
  );

  const sortedComments = [...filteredComments].sort((a, b) => {
    if (sortBy === 'sentiment') {
      return b.sentiment - a.sentiment;
    } else {
      return b.score - a.score;
    }
  });

  const getSentimentColor = (score) => {
    if (score >= 0.5) return 'text-success';
    if (score >= 0) return 'text-success-emphasis';
    if (score >= -0.5) return 'text-danger-emphasis';
    return 'text-danger';
  };

  if (!comments || comments.length === 0) {
    return (
      <div className="bg-light p-4 rounded d-flex justify-content-center align-items-center" style={{ height: '16rem' }}>
        <p className="text-muted mb-0">No comments available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 row gy-2 align-items-center">
        <div className="col-md-auto">
          <label htmlFor="sort-by" className="form-label me-2">Sort by:</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="form-select"
          >
            <option value="score">Upvotes</option>
            <option value="sentiment">Sentiment</option>
          </select>
        </div>

        <div className="col">
          <input
            type="text"
            placeholder="Search comments..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="form-control"
          />
        </div>
      </div>

      <div className="vstack gap-4">
        {sortedComments.map((comment) => (
          <div 
            key={comment.id} 
            className="border rounded p-4 bg-white shadow-sm"
          >
            <div className="d-flex justify-content-between align-items-start mb-3">
              <div className="d-flex gap-3">
                <div className="bg-light p-2 rounded text-center" style={{ minWidth: '4rem' }}>
                  <div className="h5 mb-0">{comment.score}</div>
                  <small className="text-muted">upvotes</small>
                </div>
                <div className={`bg-light p-2 rounded text-center ${getSentimentColor(comment.sentiment)}`} style={{ minWidth: '4rem' }}>
                  <div className="h5 mb-0">{comment.sentiment.toFixed(1)}</div>
                  <small className="text-muted">sentiment</small>
                </div>
              </div>
              <div className="text-muted small">
                {new Date(comment.created_utc).toLocaleDateString()}
              </div>
            </div>

            <div className="mb-3">
              <p className="mb-0 white-space-pre-line">{comment.body}</p>
            </div>

            <hr />
            <div className="mb-2">
              <strong className="d-block text-secondary mb-1">Summary:</strong>
              <p className="mb-0 text-muted">{comment.summary}</p>
            </div>

            <div className="mt-3 d-flex flex-wrap gap-2">
              {comment.themes.map((theme, index) => (
                <span 
                  key={index}
                  className="badge bg-primary-subtle text-primary-emphasis"
                >
                  {theme}
                </span>
              ))}
            </div>
          </div>
        ))}

        {sortedComments.length === 0 && (
          <div className="text-center py-5 text-muted">
            No comments match your search
          </div>
        )}
      </div>
    </div>
  );
}

export default TopComments;
