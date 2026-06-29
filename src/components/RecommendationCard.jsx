import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export default function RecommendationCard({ mode }) {
  const [recommendations, setRecommendations] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, [mode]);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/recommendations`);
      setRecommendations(response.data.recommendations);
    } catch (err) {
      console.error('Failed to fetch recommendations', err);
    }
  };

  if (!recommendations || !recommendations[mode]) {
    return null;
  }

  const rec = recommendations[mode];

  return (
    <div
      style={{
        padding: '1rem',
        marginBottom: '1rem',
        backgroundColor: 'rgba(76, 175, 80, 0.08)',
        border: '1px solid rgba(76, 175, 80, 0.4)',
        borderRadius: '8px',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ color: '#4caf50', margin: '0 0 0.5rem 0' }}>
            {rec.title}
          </h4>
          <p style={{ color: '#a0a0a0', fontSize: '0.9rem', margin: 0 }}>
            💡 {rec.hint}
          </p>
        </div>
        <div style={{ fontSize: '1.5rem', color: '#4caf50' }}>
          {expanded ? '▼' : '▶'}
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(76, 175, 80, 0.3)' }}>
          <div style={{ marginBottom: '1rem' }}>
            <h5 style={{ color: '#4caf50', marginTop: 0 }}>📊 Expected Performance:</h5>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
              <div style={{ padding: '0.8rem', backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '4px' }}>
                <p style={{ margin: '0 0 0.3rem 0', color: '#a0a0a0', fontSize: '0.85rem' }}>
                  Payload Size:
                </p>
                <p style={{ margin: 0, color: '#00d4ff', fontWeight: 'bold' }}>
                  {rec.expected_size}
                </p>
              </div>
              <div style={{ padding: '0.8rem', backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '4px' }}>
                <p style={{ margin: '0 0 0.3rem 0', color: '#a0a0a0', fontSize: '0.85rem' }}>
                  Success Rate:
                </p>
                <p style={{ margin: 0, color: '#4caf50', fontWeight: 'bold' }}>
                  {rec.success_rate || rec.survival_rate}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h5 style={{ color: '#4caf50', marginTop: 0 }}>✓ Best Practice Tips:</h5>
            <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem', color: '#a0a0a0' }}>
              {rec.tips.map((tip, idx) => (
                <li key={idx} style={{ marginBottom: '0.4rem', fontSize: '0.9rem' }}>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
