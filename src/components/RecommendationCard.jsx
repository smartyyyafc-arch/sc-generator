import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ChevronRightIcon } from './Icons';
import { API_BASE } from '../config';

export default function RecommendationCard({ mode }) {
  const [recommendations, setRecommendations] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get(`${API_BASE}/recommendations`);
        setRecommendations(response.data.recommendations);
      } catch (err) {
        console.error('Failed to fetch recommendations', err);
      }
    };
    fetchRecommendations();
  }, [mode]);

  if (!recommendations || !recommendations[mode]) return null;

  const rec = recommendations[mode];

  return (
    <div className="rec-card" onClick={() => setExpanded(!expanded)}>
      <div className="rec-header">
        <div>
          <div className="rec-title">{rec.title}</div>
          <div className="rec-hint">{rec.hint}</div>
        </div>
        <div className={`rec-expand ${expanded ? 'open' : ''}`}>
          <ChevronRightIcon size={16} />
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-default)' }}>
          <div className="stat-grid" style={{ marginBottom: '0.75rem' }}>
            <div className="stat-card">
              <div className="stat-label">Payload Size</div>
              <div className="stat-value" style={{ fontSize: '0.8125rem' }}>{rec.expected_size}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Success Rate</div>
              <div className="stat-value" style={{ fontSize: '0.8125rem', color: 'var(--success)' }}>
                {rec.success_rate || rec.survival_rate}
              </div>
            </div>
          </div>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.8125rem', lineHeight: '1.6' }}>
            {rec.tips.map((tip, idx) => <li key={idx}>{tip}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
