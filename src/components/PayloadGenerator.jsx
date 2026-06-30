import React from 'react';

export default function PayloadGenerator({
  techniques,
  selectedTechnique,
  onTechniqueChange,
  obfuscationLevel,
  onObfuscationChange,
  options,
  onOptionsChange,
  techniqueMetadata,
}) {
  const metadata = techniqueMetadata || {};

  const handleCheckboxChange = (key) => {
    onOptionsChange({
      ...options,
      [key]: !options[key],
    });
  };

  const currentMeta = metadata[selectedTechnique] || {};
  const isRecommended = currentMeta.recommended;

  return (
    <div>
      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
          onChange={(e) => onTechniqueChange(e.target.value)}
          style={{
            borderColor: isRecommended ? 'rgba(76, 175, 80, 0.5)' : undefined,
          }}
        >
          {techniques.map((tech) => (
            <option key={tech} value={tech}>
              {tech.toUpperCase()}
              {metadata[tech]?.recommended ? ' ⭐' : ''}
            </option>
          ))}
        </select>

        {currentMeta && (
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
              {currentMeta.description}
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
              <strong>Best for:</strong> {currentMeta.best_for}
            </p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Obfuscation Level:</label>
        <p style={{ fontSize: '0.85rem', color: '#a0a0a0', margin: '0.5rem 0' }}>
          💡 <strong>Recommended:</strong> Use "HIGH" for maximum protection
        </p>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['low', 'medium', 'high'].map((level) => (
            <button
              key={level}
              className={`btn-secondary ${obfuscationLevel === level ? 'active' : ''}`}
              onClick={() => onObfuscationChange(level)}
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
        <label>Advanced Options:</label>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="add-noise"
            checked={options.add_noise || false}
            onChange={() => handleCheckboxChange('add_noise')}
          />
          <label htmlFor="add-noise" style={{ margin: 0, display: 'flex', justifyContent: 'space-between' }}>
            <span>Add Noise (Confuses Analysis)</span>
            {!options.add_noise && (
              <span style={{ fontSize: '0.75rem', color: '#ffb74d' }}>Recommended ⭐</span>
            )}
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
          />
          <label htmlFor="add-comments" style={{ margin: 0 }}>
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
  );
}
