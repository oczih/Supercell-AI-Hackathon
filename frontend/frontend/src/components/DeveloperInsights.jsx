import React, { useState } from 'react';

function DeveloperInsights({ insights }) {
  const [activeCategory, setActiveCategory] = useState('bugs');
  
  if (!insights || Object.keys(insights).length === 0) {
    return (
      <div className="bg-gray-50 p-4 rounded-lg flex justify-center items-center h-64">
        <p className="text-gray-500">Developer insights not available</p>
      </div>
    );
  }

  const categories = {
    bugs: { 
      label: 'Bug Reports',
      icon: '🐛',
      description: 'Technical issues reported by users'
    },
    balance: { 
      label: 'Balance Issues',
      icon: '⚖️',
      description: 'Comments about game balance and fairness'
    },
    features: { 
      label: 'Feature Requests',
      icon: '✨',
      description: 'Suggestions for new content and gameplay mechanics'
    },
    ux: { 
      label: 'User Experience',
      icon: '🖥️',
      description: 'Interface and performance feedback'
    },
    monetization: { 
      label: 'Monetization',
      icon: '💰',
      description: 'Feedback about pricing, purchases, and value'
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2">Developer Insights</h2>
        <p className="text-gray-600">
          Top user feedback organized by category to help prioritize development efforts
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {Object.entries(categories).map(([key, { label, icon }]) => (
          <button
            key={key}
            onClick={() => setActiveCategory(key)}
            className={`px-4 py-2 rounded-md flex items-center ${
              activeCategory === key 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            <span className="mr-2">{icon}</span>
            <span>{label}</span>
            <span className="ml-2 bg-white bg-opacity-20 px-2 rounded-full text-sm">
              {insights[key]?.length || 0}
            </span>
          </button>
        ))}
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">{categories[activeCategory].icon}</span>
          <div>
            <h3 className="text-xl font-semibold">{categories[activeCategory].label}</h3>
            <p className="text-gray-600">{categories[activeCategory].description}</p>
          </div>
        </div>

        <div className="space-y-4">
          {insights[activeCategory] && insights[activeCategory].length > 0 ? (
            insights[activeCategory].map((item, index) => (
              <div key={index} className="bg-white p-4 rounded-md border border-gray-200">
                <div className="flex justify-between mb-2">
                  <div className="flex items-center">
                    <span className="font-medium text-gray-800">User Feedback</span>
                    <span className={`ml-3 px-2 py-1 rounded text-xs ${
                      item.sentiment >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      Sentiment: {item.sentiment.toFixed(1)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Score: {item.score}
                  </div>
                </div>

                <div className="mb-3 text-gray-700 bg-gray-50 p-3 rounded border border-gray-100">
                  <p className="whitespace-pre-line">{item.text}</p>
                </div>

                <div>
                  <p className="font-medium text-gray-700">Summary:</p>
                  <p className="text-gray-600">{item.summary}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No insights available for this category
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeveloperInsights;
