import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Toast from './Toast';

const API_BASE = 'http://localhost:5000/api';

export default function TechniqueSelector({
  techniques = [],
  selectedTechnique,
  onTechniqueChange,
  showMetadata = true,
  compact = false,
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState({});
  const [toast, setToast] = useState(null);
  const [isHoveredTechnique, setIsHoveredTechnique] = useState(null);
  const abortControllerRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    fetchTechniqueMetadata();

    return () => {
      mountedRef.current = false;
      // Clean up abort controller to prevent memory leaks
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const fetchTechniqueMetadata = async () => {
    abortControllerRef.current = new AbortController();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_BASE}/techniques`, {
        signal: abortControllerRef.current.signal,
        timeout: 10000, // 10 second timeout
      });

      // Ensure we only update state if component is still mounted
      if (!mountedRef.current) return;

      const fetchedMetadata = response.data?.metadata || {};
      setMetadata(fetchedMetadata);

      // Validate that we have data
      if (!Object.keys(fetchedMetadata).length) {
        setError('No technique metadata available');
      }
    } catch (err) {
      if (!mountedRef.current) return;

      // Don't handle abort errors
      if (err.name === 'CanceledError') {
        return;
      }

      const errorMessage = getErrorMessage(err);
      console.error('Failed to fetch technique metadata:', err);
      setError(errorMessage);

      setToast({
        message: `Error loading techniques: ${errorMessage}`,
        type: 'error',
      });
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  };

  const getErrorMessage = (error) => {
    if (!error) return 'Unknown error occurred';

    // API error response
    if (error.response?.data?.error) {
      return error.response.data.error;
    }

    // HTTP status codes
    if (error.response?.status === 404) {
      return 'API endpoint not found (404)';
    }

    if (error.response?.status === 500) {
      return 'Server error (500) - please try again later';
    }

    if (error.response?.status === 503) {
      return 'Service unavailable (503) - server is down';
    }

    // Network errors
    if (error.code === 'ECONNABORTED') {
      return 'Request timeout - server took too long to respond';
    }

    if (error.code === 'ERR_NETWORK') {
      return 'Network error - unable to reach server';
    }

    if (error.message === 'Network Error') {
      return 'Network connection failed';
    }

    // Fallback to error message
    if (error.message) {
      return error.message;
    }

    return 'Failed to fetch technique data';
  };

  const handleTechniqueChange = (newTechnique) => {
    try {
      if (!newTechnique || typeof newTechnique !== 'string') {
        throw new Error('Invalid technique selected');
      }

      onTechniqueChange(newTechnique);

      // Show success feedback
      setToast({
        message: `Switched to ${newTechnique.toUpperCase()} technique`,
        type: 'info',
      });
    } catch (err) {
      console.error('Error changing technique:', err);
      setToast({
        message: 'Failed to change encoding technique',
        type: 'error',
      });
    }
  };

  const handleRetry = () => {
    fetchTechniqueMetadata();
  };

  const currentMeta = metadata[selectedTechnique] || {};
  const hasMetadata = Object.keys(currentMeta).length > 0;
  const isRecommended = currentMeta.recommended === true;

  // Determine if we have any techniques to display
  const hasTechniques = techniques && techniques.length > 0;

  return (
    <>
      <div
        style={{
          opacity: loading && !compact ? 0.7 : 1,
          transition: 'opacity 0.3s ease',
          pointerEvents: loading && !compact ? 'none' : 'auto',
        }}
      >
        {/* Error State */}
        {error && !loading && (
          <div
            style={{
              marginBottom: '1rem',
              padding: '1rem',
              backgroundColor: 'rgba(255, 107, 107, 0.15)',
              border: '1px solid rgba(255, 107, 107, 0.5)',
              borderRadius: '6px',
              color: '#ff6b6b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: 1 }}>
              <p style={{ margin: '0 0 0.5rem 0', fontWeight: '600', fontSize: '0.9rem' }}>
                ⚠️ Error Loading Techniques
              </p>
              <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.9 }}>
                {error}
              </p>
            </div>
            <button
              onClick={handleRetry}
              style={{
                marginLeft: '1rem',
                padding: '0.5rem 1rem',
                backgroundColor: 'rgba(255, 107, 107, 0.3)',
                border: '1px solid rgba(255, 107, 107, 0.5)',
                color: '#ff6b6b',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.85rem',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 107, 107, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 107, 107, 0.3)';
              }}
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              color: '#a0a0a0',
            }}
          >
            <div
              className="spinner"
              style={{
                display: 'inline-block',
                marginRight: '0.8rem',
                marginBottom: '0.5rem',
              }}
            ></div>
            <p style={{ margin: 0, fontSize: '0.95rem' }}>
              Loading encoding techniques...
            </p>
            <p style={{ margin: '0.3rem 0 0 0', fontSize: '0.8rem', opacity: 0.8 }}>
              Please wait while we fetch available options
            </p>
          </div>
        )}

        {/* Main Content */}
        {!loading && (
          <>
            {/* Technique Label and Status */}
            <div style={{ marginBottom: '1rem' }}>
              <label
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  color: '#00d4ff',
                  fontWeight: '600',
                  fontSize: '0.9rem',
                  marginBottom: '0.5rem',
                }}
              >
                <span>Encoding Technique</span>
                {isRecommended && (
                  <span
                    style={{
                      fontSize: '0.75rem',
                      padding: '0.3rem 0.8rem',
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

              {/* Technique Selection */}
              {hasTechniques ? (
                <div
                  style={{
                    display: compact ? 'flex' : 'grid',
                    gridTemplateColumns: compact ? undefined : '1fr',
                    gap: '0.6rem',
                    flexWrap: 'wrap',
                  }}
                >
                  {techniques.map((technique) => {
                    const techMeta = metadata[technique] || {};
                    const isSelected = selectedTechnique === technique;
                    const isTechRecommended = techMeta.recommended === true;

                    return (
                      <button
                        key={technique}
                        onClick={() => handleTechniqueChange(technique)}
                        onMouseEnter={() => setIsHoveredTechnique(technique)}
                        onMouseLeave={() => setIsHoveredTechnique(null)}
                        style={{
                          padding: compact ? '0.6rem 1rem' : '0.8rem 1rem',
                          backgroundColor: isSelected
                            ? 'rgba(0, 212, 255, 0.2)'
                            : 'rgba(0, 212, 255, 0.05)',
                          border: isSelected || isHoveredTechnique === technique
                            ? '1px solid #00d4ff'
                            : '1px solid rgba(0, 212, 255, 0.2)',
                          color: isSelected ? '#00d4ff' : '#e0e0e0',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontWeight: isSelected ? '600' : '500',
                          fontSize: compact ? '0.85rem' : '0.95rem',
                          transition: 'all 0.2s ease',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          boxShadow: isSelected
                            ? '0 0 12px rgba(0, 212, 255, 0.2)'
                            : 'none',
                          position: 'relative',
                          overflow: 'hidden',
                        }}
                      >
                        {technique.toUpperCase()}
                        {isTechRecommended && ' ⭐'}
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div
                  style={{
                    padding: '1rem',
                    backgroundColor: 'rgba(255, 193, 7, 0.15)',
                    border: '1px solid rgba(255, 193, 7, 0.5)',
                    borderRadius: '6px',
                    color: '#ffc107',
                    fontSize: '0.9rem',
                  }}
                >
                  ⚠️ No encoding techniques available
                </div>
              )}
            </div>

            {/* Technique Metadata Display */}
            {showMetadata && selectedTechnique && hasMetadata && (
              <div
                style={{
                  padding: '1rem',
                  backgroundColor: 'rgba(0, 212, 255, 0.08)',
                  border: '1px solid rgba(0, 212, 255, 0.3)',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                }}
              >
                {/* Description */}
                <p style={{ margin: '0 0 0.8rem 0', color: '#a0a0a0', lineHeight: 1.4 }}>
                  {currentMeta.description || 'No description available'}
                </p>

                {/* Metadata Grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '1rem',
                    marginBottom: '0.8rem',
                  }}
                >
                  {/* Detection Resistance */}
                  <div>
                    <p style={{ margin: '0 0 0.3rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
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

                  {/* Size Overhead */}
                  <div>
                    <p style={{ margin: '0 0 0.3rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                      Size Overhead:
                    </p>
                    <p style={{ margin: 0, color: '#00d4ff', fontWeight: 'bold', fontSize: '0.9rem' }}>
                      {currentMeta.size_overhead || 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Best For */}
                {currentMeta.best_for && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <p style={{ margin: '0 0 0.2rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                      <strong>Best for:</strong>
                    </p>
                    <p style={{ margin: 0, color: '#e0e0e0', fontSize: '0.85rem' }}>
                      {currentMeta.best_for}
                    </p>
                  </div>
                )}

                {/* Compatibility */}
                {currentMeta.compatibility && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <p style={{ margin: '0 0 0.2rem 0', color: '#a0a0a0', fontSize: '0.8rem' }}>
                      <strong>Compatibility:</strong>
                    </p>
                    <p style={{ margin: 0, color: '#e0e0e0', fontSize: '0.85rem' }}>
                      {Array.isArray(currentMeta.compatibility)
                        ? currentMeta.compatibility.join(', ')
                        : currentMeta.compatibility}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* No Selection State */}
            {showMetadata && !selectedTechnique && hasTechniques && (
              <div
                style={{
                  padding: '1.5rem',
                  textAlign: 'center',
                  backgroundColor: 'rgba(0, 212, 255, 0.05)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  borderRadius: '6px',
                  color: '#a0a0a0',
                }}
              >
                <p style={{ margin: 0, fontSize: '0.9rem' }}>
                  Select an encoding technique to view details
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Toast Notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          autoClose={true}
          autoCloseDelay={4000}
        />
      )}
    </>
  );
}
