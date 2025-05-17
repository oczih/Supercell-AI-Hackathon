import React, { useState } from 'react';

function DeveloperInsights({ insights }) {
  const [activeCategory, setActiveCategory] = useState('bugs');
  
  if (!insights || Object.keys(insights).length === 0) {
    return (
      <div className="bg-light p-4 rounded d-flex justify-content-center align-items-center" style={{ height: '16rem' }}>
        <p className="text-muted mb-0">Developer insights not available</p>
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
      <div className="mb-4">
        <h2 className="h4 fw-bold mb-2">Developer Insights</h2>
        <p className="text-muted">
          Top user feedback organized by category to help prioritize development efforts
        </p>
      </div>

      <div className="mb-4 d-flex flex-wrap gap-2">
        {Object.entries(categories).map(([key, { label, icon }]) => (
          <button
            key={key}
            onClick={() => setActiveCategory(key)}
            className={`btn d-flex align-items-center ${activeCategory === key ? 'btn-primary text-white' : 'btn-light text-dark border'}`}
          >
            <span className="me-2">{icon}</span>
            <span>{label}</span>
            <span className="ms-2 badge bg-secondary">
              {insights[key]?.length || 0}
            </span>
          </button>
        ))}
      </div>

      <div className="bg-light rounded p-4">
        <div className="d-flex align-items-center mb-3">
          <span className="fs-4 me-3">{categories[activeCategory].icon}</span>
          <div>
            <h3 className="h5 fw-semibold mb-0">{categories[activeCategory].label}</h3>
            <p className="text-muted mb-0">{categories[activeCategory].description}</p>
          </div>
        </div>

        <div className="d-grid gap-3">
          {insights[activeCategory] && insights[activeCategory].length > 0 ? (
            insights[activeCategory].map((item, index) => (
              <div key={index} className="bg-white p-3 rounded border">
                <div className="d-flex justify-content-between mb-2">
                  <div className="d-flex align-items-center">
                    <span className="fw-medium text-dark">User Feedback</span>
                    <span className={`ms-3 px-2 py-1 rounded text-sm ${item.sentiment >= 0 ? 'bg-success bg-opacity-10 text-success' : 'bg-danger bg-opacity-10 text-danger'}`}>
                      Sentiment: {item.sentiment.toFixed(1)}
                    </span>
                  </div>
                  <div className="text-muted small">
                    Score: {item.score}
                  </div>
                </div>

                <div className="mb-3 text-dark bg-light p-3 rounded border">
                  <p className="mb-0" style={{ whiteSpace: 'pre-line' }}>{item.text}</p>
                </div>

                <div>
                  <p className="fw-medium text-dark mb-1">Summary:</p>
                  <p className="text-muted mb-0">{item.summary}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-muted">
              No insights available for this category
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeveloperInsights;
