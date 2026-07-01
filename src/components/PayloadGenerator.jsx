import React from 'react';
import { CodeIcon } from './Icons';

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
  const currentMeta = metadata[selectedTechnique] || {};
  const isRecommended = currentMeta.recommended;

  const handleCheckboxChange = (key) => {
    onOptionsChange({ ...options, [key]: !options[key] });
  };

  return (
    <div>
      <h2><CodeIcon /> Encoding Technique</h2>
      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Technique</span>
          {isRecommended && <span className="tag success">Recommended</span>}
        </label>
        <select
          value={selectedTechnique}
          onChange={(e) => onTechniqueChange(e.target.value)}
        >
          {techniques.map((tech) => (
            <option key={tech} value={tech}>
              {tech.toUpperCase()}{metadata[tech]?.recommended ? ' *' : ''}
            </option>
          ))}
        </select>

        {currentMeta.description && (
          <div className="info-box neutral" style={{ marginTop: '0.625rem' }}>
            <p style={{ margin: '0 0 0.375rem 0', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
              {currentMeta.description}
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem' }}>
              <div>
                <div className="stat-label">Detection Resistance</div>
                <div style={{
                  fontWeight: 600, fontSize: '0.8125rem',
                  color: currentMeta.detection_resistance?.includes('high') ? 'var(--success)' : 'var(--warning)',
                }}>
                  {currentMeta.detection_resistance || 'N/A'}
                </div>
              </div>
              <div>
                <div className="stat-label">Size Overhead</div>
                <div style={{ fontWeight: 600, fontSize: '0.8125rem', color: 'var(--accent)' }}>
                  {currentMeta.size_overhead || 'N/A'}
                </div>
              </div>
            </div>
            {currentMeta.best_for && (
              <p style={{ margin: '0.375rem 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Best for: {currentMeta.best_for}
              </p>
            )}
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Obfuscation Level</label>
        <div className="level-buttons">
          {['low', 'medium', 'high'].map((level) => (
            <button
              key={level}
              className={`level-btn ${obfuscationLevel === level ? 'active' : ''}`}
              onClick={() => onObfuscationChange(level)}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Options</label>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="add-noise"
            checked={options.add_noise || false}
            onChange={() => handleCheckboxChange('add_noise')}
          />
          <label htmlFor="add-noise">Add noise (confuses analysis)</label>
        </div>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="add-comments"
            checked={options.add_comments || false}
            onChange={() => handleCheckboxChange('add_comments')}
          />
          <label htmlFor="add-comments">Add comments (looks legitimate)</label>
        </div>
      </div>
    </div>
  );
}
