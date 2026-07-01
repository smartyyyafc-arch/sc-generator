import React, { useState } from 'react';
import { FingerprintIcon, PlusIcon, XIcon } from './Icons';

export default function FingerprintSelector({
  fingerprints,
  selectedFingerprint,
  onSelectFingerprint,
  onCreateFingerprint,
}) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newFP, setNewFP] = useState({ name: '', description: '' });

  const handleCreateClick = async () => {
    if (!newFP.name) return;
    const config = {
      description: newFP.description,
      modifications: { pe_sections: { add_junk: true }, randomize_all: true },
    };
    const id = await onCreateFingerprint(newFP.name, config);
    if (id) {
      setNewFP({ name: '', description: '' });
      setShowCreateForm(false);
    }
  };

  return (
    <div>
      <h2><FingerprintIcon /> Fingerprinting</h2>
      <div className="form-group">
        <label>Select Profile</label>
        <div className="fingerprint-grid">
          {fingerprints.map((fp) => (
            <div
              key={fp.id}
              className={`fingerprint-card ${selectedFingerprint === fp.id ? 'selected' : ''}`}
              onClick={() => onSelectFingerprint(fp.id)}
            >
              <div className="fingerprint-name">{fp.name}</div>
              <div className="fingerprint-desc">{fp.description}</div>
            </div>
          ))}
        </div>
      </div>

      <button
        className="btn-secondary"
        onClick={() => setShowCreateForm(!showCreateForm)}
        style={{ width: '100%' }}
      >
        {showCreateForm ? <><XIcon size={14} /> Cancel</> : <><PlusIcon size={14} /> Custom Profile</>}
      </button>

      {showCreateForm && (
        <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-default)' }}>
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={newFP.name}
              onChange={(e) => setNewFP({ ...newFP, name: e.target.value })}
              placeholder="e.g., Office 2019"
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Description</label>
            <input
              type="text"
              value={newFP.description}
              onChange={(e) => setNewFP({ ...newFP, description: e.target.value })}
              placeholder="Optional"
            />
          </div>
          <button className="btn-primary" onClick={handleCreateClick} style={{ width: '100%', marginTop: '0.75rem' }}>
            Create
          </button>
        </div>
      )}

      {!selectedFingerprint && (
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.625rem' }}>
          Optional. Modifies file signatures to evade detection.
        </p>
      )}
    </div>
  );
}
