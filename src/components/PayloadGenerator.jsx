import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Toast from './Toast';

const API_BASE = 'http://localhost:5000/api';

export default function PayloadGenerator({
  techniques,
  selectedTechnique,
  onTechniqueChange,
  obfuscationLevel,
  onObfuscationChange,
  options,
  onOptionsChange,
}) {
  const [metadata, setMetadata] = useState({});
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    fetchTechniqueMetadata();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const fetchTechniqueMetadata = async () => {
    abortControllerRef.current = new AbortController();
    setLoading(true);

    try {
      const response = await axios.get(`${API_BASE}/techniques`, {
        signal: abortControllerRef.current.signal,
      });
      setMetadata(response.data.metadata || {});
    } catch (err) {
      if (err.name === 'CanceledError') {
        return;
      }

      const errorMessage = getErrorMessage(err);
      console.error('Failed to fetch technique metadata:', err);
      setToast({
        message: `Error loading techniques: ${errorMessage}`,
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const getErrorMessage = (error) => {
    if (!error) return 'Unknown error occurred';

    if (error.response?.data?.error) {
      return error.response.data.error;
    }

    if (error.response?.status === 404) {
      return 'API endpoint not found (404)';
    }

    if (error.response?.status === 500) {
      return 'Server error (500)';
    }

    if (error.response?.status === 503) {
      return 'Service unavailable (503)';
    }

    if (error.code === 'ECONNABORTED') {
      return 'Request timeout';
    }

    if (error.code === 'ERR_NETWORK') {
      return 'Network error - unable to reach server';
    }

    if (error.message) {
      return error.message;
    }

    return 'Failed to fetch data';
  };

  const handleCheckboxChange = (key) => {
    try {
      onOptionsChange({
        ...options,
        [key]: !options[key],
      });
    } catch (err) {
      console.error('Error updating options:', err);
      setToast({
        message: 'Failed to update options',
        type: 'error',
      });
    }
  };

  const handleTechniqueChange = (newTechnique) => {
    try {
      onTechniqueChange(newTechnique);
    } catch (err) {
      console.error('Error changing technique:', err);
      setToast({
        message: 'Failed to change encoding technique',
        type: 'error',
      });
    }
  };

  const handleObfuscationChange = (level) => {
    try {
      onObfuscationChange(level);
    } catch (err) {
      console.error('Error changing obfuscation level:', err);
      setToast({
        message: 'Failed to change obfuscation level',
        type: 'error',
      });
    }
  };

  const currentMeta = metadata[selectedTechnique] || {};
  const isRecommended = currentMeta.recommended;

  return (
    <>
      <div style={{ opacity: loading ? 0.6 : 1, transition: 'opacity 0.2s ease' }}>
        <div className="form-group">
          <label
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              opacity: loading ? 0.7 : 1,
            }}
          >
            <span>Encoding Technique</span>
            {isRecommended && (
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '0.3rem 0.6rem',
                  backgroundColor: 'rgba(76, 175, 80, 0.3)',
                  border: '1px solid rgba(76, 175, 80, 0.6)',
                  borderRadius: '4px',
                  color: '#4caf50',
                  fontWeight: 'bold',
                }}
              >
                ⭐ RECOMMENDED
              </span>
            )}
          </label>
          <select
            value={selectedTechnique}
            onChange={(e) => handleTechniqueChange(e.target.value)}
            disabled={loading}
            style={{
              borderColor: isRecommended ? 'rgba(76, 175, 80, 0.5)' : undefined,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {techniques && techniques.length > 0 ? (
              techniques.map((tech) => (
                <option key={tech} value={tech}>
                  {tech.toUpperCase()}
                  {metadata[tech]?.recommended ? ' ⭐' : ''}
                </option>
              ))
            ) : (
              <option disabled>No techniques available</option>
            )}
          </select>

          {currentMeta && Object.keys(currentMeta).length > 0 && (
            <div
              style={{
                marginTop: '0.8rem',
                padding: '0.8rem',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: '6px',
                fontSize: '0.85rem',
              }}
            >
              <p style={{ margin: '0 0 0.5rem 0', color: '#a0a0a0' }}>
                {currentMeta.description || 'No description available'}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div>
                  <p style={{ margin: '0 0 0.2rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                    Detection Resistance:
                  </p>
                  <p
                    style={{
                      margin: 0,
                      color:
                        currentMeta.detection_resistance?.includes('very-high') ||
                        currentMeta.detection_resistance?.includes('high')
                          ? '#4caf50'
                          : '#ffb74d',
                      fontWeight: 'bold',
                      fontSize: '0.9rem',
                    }}
                  >
                    {currentMeta.detection_resistance || 'N/A'}
                  </p>
                </div>
                <div>
                  <p style={{ margin: '0 0 0.2rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                    Size Overhead:
                  </p>
                  <p style={{ margin: 0, color: '#00d4ff', fontWeight: 'bold', fontSize: '0.9rem' }}>
                    {currentMeta.size_overhead || 'N/A'}
                  </p>
                </div>
              </div>
              <p style={{ margin: '0.5rem 0 0 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                <strong>Best for:</strong> {currentMeta.best_for || 'General use'}
              </p>
            </div>
          )}

          {loading && (
            <div style={{ marginTop: '0.8rem', padding: '0.8rem', textAlign: 'center', color: '#a0a0a0' }}>
              <div className="spinner" style={{ display: 'inline-block', marginRight: '0.5rem' }}></div>
              Loading techniques...
            </div>
          )}
        </div>

        <div className="form-group">
          <label style={{ opacity: loading ? 0.7 : 1 }}>Obfuscation Level:</label>
          <p style={{ fontSize: '0.85rem', color: '#a0a0a0', margin: '0.5rem 0' }}>
            💡 <strong>Recommended:</strong> Use "HIGH" for maximum protection
          </p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {['low', 'medium', 'high'].map((level) => (
              <button
                key={level}
                className={`btn-secondary ${obfuscationLevel === level ? 'active' : ''}`}
                onClick={() => handleObfuscationChange(level)}
                disabled={loading}
                style={{
                  flex: 1,
                  textTransform: 'capitalize',
                  backgroundColor:
                    obfuscationLevel === level
                      ? 'rgba(0, 212, 255, 0.3)'
                      : 'rgba(0, 212, 255, 0.05)',
                  borderColor:
                    level === 'high' && obfuscationLevel !== 'high'
                      ? 'rgba(76, 175, 80, 0.5)'
                      : undefined,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {level === 'low' && '🟢 Low (Fast)'}
                {level === 'medium' && '🟡 Medium (Balanced)'}
                {level === 'high' && '🔴 High (Secure)'}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label style={{ opacity: loading ? 0.7 : 1 }}>Advanced Options:</label>
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="add-noise"
              checked={options.add_noise || false}
              onChange={() => handleCheckboxChange('add_noise')}
              disabled={loading}
              style={{ cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}
            />
            <label
              htmlFor="add-noise"
              style={{
                margin: 0,
                display: 'flex',
                justifyContent: 'space-between',
                opacity: loading ? 0.7 : 1,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              <span>Add Noise (Confuses Analysis)</span>
              {!options.add_noise && <span style={{ fontSize: '0.75rem', color: '#ffb74d' }}>Recommended ⭐</span>}
            </label>
          </div>
          {options.add_noise && (
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.4rem 0 0 0' }}>
              ✓ Adds dead code to confuse analysis tools
            </p>
          )}

          <div className="checkbox-group" style={{ marginTop: '0.6rem' }}>
            <input
              type="checkbox"
              id="add-comments"
              checked={options.add_comments || false}
              onChange={() => handleCheckboxChange('add_comments')}
              disabled={loading}
              style={{ cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}
            />
            <label
              htmlFor="add-comments"
              style={{
                margin: 0,
                opacity: loading ? 0.7 : 1,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              Add Comments (Looks more legitimate)
            </label>
          </div>
          {options.add_comments && (
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.4rem 0 0 0' }}>
              ✓ Adds system-like comments to appear legitimate
            </p>
          )}
        </div>

        <div
          style={{
            marginTop: '1rem',
            padding: '1rem',
            backgroundColor: 'rgba(76, 175, 80, 0.08)',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            borderRadius: '6px',
            fontSize: '0.85rem',
            color: '#a0a0a0',
            opacity: loading ? 0.7 : 1,
          }}
        >
          <p style={{ margin: '0 0 0.5rem 0', color: '#4caf50', fontWeight: 'bold' }}>
            ✓ Best Practice Configuration:
          </p>
          <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
            <li>Use a ⭐ RECOMMENDED technique for best results</li>
            <li>Always set obfuscation to HIGH</li>
            <li>Enable "Add Noise" for maximum evasion</li>
            <li>Expected payload size: 8-15 KB</li>
          </ul>
        </div>
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          autoClose={true}
          autoCloseDelay={5000}
        />
      )}
    </>
  );
}
