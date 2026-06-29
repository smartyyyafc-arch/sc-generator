import React from 'react';

export default function PayloadGenerator({
  techniques,
  selectedTechnique,
  onTechniqueChange,
  obfuscationLevel,
  onObfuscationChange,
  options,
  onOptionsChange,
}) {
  const handleCheckboxChange = (key) => {
    onOptionsChange({
      ...options,
      [key]: !options[key],
    });
  };

  return (
    <div>
      <div className="form-group">
        <label>Technique:</label>
        <select
          value={selectedTechnique}
          onChange={(e) => onTechniqueChange(e.target.value)}
        >
          {techniques.map((tech) => (
            <option key={tech} value={tech}>
              {tech.toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Obfuscation Level:</label>
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
              }}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Additional Options:</label>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="add-comments"
            checked={options.add_comments || false}
            onChange={() => handleCheckboxChange('add_comments')}
          />
          <label htmlFor="add-comments" style={{ margin: 0 }}>
            Add Comments
          </label>
        </div>
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="add-noise"
            checked={options.add_noise || false}
            onChange={() => handleCheckboxChange('add_noise')}
          />
          <label htmlFor="add-noise" style={{ margin: 0 }}>
            Add Noise
          </label>
        </div>
      </div>

      <div style={{ fontSize: '0.85rem', color: '#a0a0a0', marginTop: '1rem' }}>
        <p>
          <strong>💡 Tip:</strong> Different techniques have varying detection
          resistance. Experiment to find the best match for your target.
        </p>
      </div>
    </div>
  );
}
