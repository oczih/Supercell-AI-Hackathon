
import React, { useState } from 'react';

function TopComments({ comments }) {
  const [sortBy, setSortBy] = useState('score');
  const [searchText, setSearchText] = useState('');

  // Filter comments by search text
  const filteredComments = comments.filter(comment => 
    comment.body.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.summary.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.themes.some(theme => theme.toLowerCase().includes(searchText.toLowerCase()))
  );

  // Sort comments
  const sortedComments = [...filteredComments].sort((a, b) => {
    if (sortBy === 'sentiment') {
      return b.sentiment - a.sentiment;
    } else {
      return b.score - a.score;
    }
  });

  // Sentiment color based on score
  const getSentimentColor = (score) => {
    if (score >= 0.5) return 'text-green-600';
    if (score >= 0) return 'text-green-400';
    if (score >= -0.5) return 'text-red-400';
    return 'text-red-600';
  };

  if (!comments || comments.length === 0) {
    return (
      <div className="bg-gray-50 p-4 rounded-lg flex justify-center items-center h-64">
        <p className="text-gray-500">No comments available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        <div>
          <label htmlFor="sort-by" className="mr-2 text-gray-700">Sort by:</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="score">Upvotes</option>
            <option value="sentiment">Sentiment</option>
          </select>
        </div>

        <div className="flex-grow">
          <input
            type="text"
            placeholder="Search comments..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="w-full px-4 py-2 border rounded-md"
          />
        </div>
      </div>

      <div className="space-y-6">
        {sortedComments.map((comment) => (
          <div 
            key={comment.id} 
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex gap-3">
                <div className="bg-gray-100 p-2 rounded-md text-center min-w-16">
                  <div className="text-xl font-bold">{comment.score}</div>
                  <div className="text-xs text-gray-500">upvotes</div>
                </div>
                <div className={`bg-gray-100 p-2 rounded-md text-center min-w-16 ${getSentimentColor(comment.sentiment)}`}>
                  <div className="text-xl font-bold">{comment.sentiment.toFixed(1)}</div>
                  <div className="text-xs text-gray-500">sentiment</div>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {new Date(comment.created_utc).toLocaleDateString()}
              </div>
            </div>

            <div className="mb-3">
              <p className="text-gray-800 whitespace-pre-line">{comment.body}</p>
            </div>

            <div className="border-t pt-2">
              <p className="font-medium text-gray-700 mb-2">Summary:</p>
              <p className="text-gray-600">{comment.summary}</p>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {comment.themes.map((theme, index) => (
                <span 
                  key={index}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs"
                >
                  {theme}
                </span>
              ))}
            </div>
          </div>
        ))}

        {sortedComments.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No comments match your search
          </div>
        )}
      </div>
    </div>
  );
}

export default TopComments;