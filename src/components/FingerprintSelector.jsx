import React, { useState } from 'react';

export default function FingerprintSelector({
  fingerprints,
  selectedFingerprint,
  onSelectFingerprint,
  onCreateFingerprint,
}) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newFP, setNewFP] = useState({
    name: '',
    description: '',
  });

  const handleCreateClick = async () => {
    if (!newFP.name) {
      alert('Please enter a fingerprint name');
      return;
    }

    const config = {
      description: newFP.description,
      modifications: {
        pe_sections: { add_junk: true },
        randomize_all: true,
      },
    };

    const id = await onCreateFingerprint(newFP.name, config);
    if (id) {
      setNewFP({ name: '', description: '' });
      setShowCreateForm(false);
    }
  };

  return (
    <div>
      <div className="form-group">
        <label>Select Fingerprint:</label>
        <div className="fingerprint-grid">
          {fingerprints.map((fp) => (
            <div
              key={fp.id}
              className={`fingerprint-card ${selectedFingerprint === fp.id ? 'selected' : ''}`}
              onClick={() => onSelectFingerprint(fp.id)}
            >
              <div className="fingerprint-name">
                {fp.name}
                {fp.is_custom && ' ⭐'}
              </div>
              <div className="fingerprint-desc">{fp.description}</div>
            </div>
          ))}
        </div>
      </div>

      <button
        className="btn-secondary"
        onClick={() => setShowCreateForm(!showCreateForm)}
        style={{ width: '100%', marginTop: '0.8rem' }}
      >
        {showCreateForm ? '✕ Cancel' : '➕ Custom Fingerprint'}
      </button>

      {showCreateForm && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(0, 212, 255, 0.05)', borderRadius: '6px' }}>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              value={newFP.name}
              onChange={(e) => setNewFP({ ...newFP, name: e.target.value })}
              placeholder="e.g., Office 2019"
            />
          </div>
          <div className="form-group">
            <label>Description:</label>
            <input
              type="text"
              value={newFP.description}
              onChange={(e) => setNewFP({ ...newFP, description: e.target.value })}
              placeholder="Optional description"
            />
          </div>
          <button
            className="btn-primary"
            onClick={handleCreateClick}
            style={{ width: '100%' }}
          >
            Create Fingerprint
          </button>
        </div>
      )}

      {!selectedFingerprint && (
        <div style={{ fontSize: '0.85rem', color: '#a0a0a0', marginTop: '0.8rem' }}>
          <p>ℹ️ Optional: Fingerprints modify file signatures to evade detection.</p>
        </div>
      )}
    </div>
  );
}
