import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LayersIcon, ShieldIcon, ZapIcon, TargetIcon, EyeIcon, SettingsIcon, CheckIcon, CopyIcon, DownloadIcon, LoaderIcon } from './Icons';
import { API_BASE } from '../config';

const PRESET_ICONS = {
  stealth_pro: EyeIcon,
  reliable_max: ShieldIcon,
  quick_deploy: ZapIcon,
  full_arsenal: TargetIcon,
  silent_persistent: LayersIcon,
};

const PRESETS = {
  stealth_pro: {
    name: 'Stealth Pro',
    icon: EyeIcon,
    description: 'Maximum stealth with anti-analysis and silent execution. Ideal for environments with active monitoring.',
    encoding: 'multi',
    installer: 'silent',
    persistence: 'registry',
    tags: ['Anti-Detection', 'Silent', 'Low Footprint'],
  },
  reliable_max: {
    name: 'Reliable Max',
    icon: ShieldIcon,
    description: 'Maximum reliability with multi-method persistence and polymorphic encoding. Best survival rate across reboots.',
    encoding: 'base64',
    installer: 'polymorphic',
    persistence: 'multi',
    tags: ['99%+ Survival', 'Polymorphic', 'Multi-Persist'],
  },
  quick_deploy: {
    name: 'Quick Deploy',
    icon: ZapIcon,
    description: 'Minimal footprint with fast deployment. Smallest payload size for bandwidth-constrained scenarios.',
    encoding: 'base64',
    installer: 'silent',
    persistence: 'startup',
    tags: ['Fast', 'Small Size', 'Simple'],
  },
  full_arsenal: {
    name: 'Full Arsenal',
    icon: TargetIcon,
    description: 'All techniques combined at maximum settings. Largest payload but highest evasion and persistence.',
    encoding: 'multi',
    installer: 'anti_analysis',
    persistence: 'multi',
    tags: ['All Techniques', 'Max Evasion', 'Max Persistence'],
  },
  silent_persistent: {
    name: 'Silent Persistent',
    icon: LayersIcon,
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
  { value: 'array', label: 'Array' },
  { value: 'wmi', label: 'WMI' },
  { value: 'registry', label: 'Registry' },
  { value: 'environment', label: 'Environment Variables' },
  { value: 'com', label: 'COM Objects' },
  { value: 'obfuscated_calls', label: 'Obfuscated Calls' },
  { value: 'filewriter', label: 'FileWriter' },
  { value: 'multi_encoding', label: 'Multi-Encoding' },
  { value: 'hidden_execution', label: 'Hidden Execution' },
  { value: 'polymorphic', label: 'Polymorphic' },
  { value: 'multi', label: 'Multi (Combined)' },
  { value: 'direct', label: 'Direct' },
];

const INSTALLER_OPTIONS = [
  { value: 'polymorphic', label: 'Polymorphic' },
  { value: 'anti_analysis', label: 'Anti-Analysis' },
  { value: 'multi_stage', label: 'Multi-Stage' },
  { value: 'silent', label: 'Silent' },
  { value: 'none', label: 'None' },
];

const PERSISTENCE_OPTIONS = [
  { value: 'registry', label: 'Registry' },
  { value: 'startup', label: 'Startup Folder' },
  { value: 'scheduled_task', label: 'Scheduled Task' },
  { value: 'wmi', label: 'WMI Event' },
  { value: 'service', label: 'Windows Service' },
  { value: 'defender', label: 'Defender Exclusion' },
  { value: 'multi', label: 'Multi-Method (All)' },
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
  const [serverOptions, setServerOptions] = useState(null);

  useEffect(() => {
    fetchCombinedOptions();
  }, []);

  const fetchCombinedOptions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/combined-options`);
      setServerOptions(response.data);
    } catch (err) {
      console.error('Failed to fetch combined options', err);
    }
  };

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

  return (
    <div>
      <h2><LayersIcon /> Combined Pipeline</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', margin: '0 0 1rem 0' }}>
        Select a preset or customize individual stages for your deployment pipeline
      </p>

      {error && <div className="error-banner">{error}</div>}

      <div className="form-group">
        <label>Deployment Presets</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.375rem' }}>
          {Object.entries(PRESETS).map(([key, preset]) => {
            const PresetIcon = preset.icon;
            return (
              <div
                key={key}
                className={`fingerprint-card ${selectedPreset === key ? 'selected' : ''}`}
                onClick={() => handlePresetSelect(key)}
              >
                <div className="fingerprint-name" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <PresetIcon size={14} />
                  {preset.name}
                </div>
                <div className="fingerprint-desc" style={{ marginBottom: '0.375rem' }}>
                  {preset.description}
                </div>
                <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
                  {preset.tags.map((tag) => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            );
          })}

          <div
            className={`fingerprint-card ${useCustom ? 'selected' : ''}`}
            onClick={handleCustomToggle}
          >
            <div className="fingerprint-name" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
              <SettingsIcon size={14} />
              Custom Configuration
            </div>
            <div className="fingerprint-desc">
              Manually select encoding, installer, and persistence options individually.
            </div>
          </div>
        </div>
      </div>

      <div style={{
        marginTop: '0.75rem',
        padding: '1rem',
        background: 'var(--accent-subtle)',
        border: '1px solid rgba(59, 130, 246, 0.2)',
        borderRadius: 'var(--radius-md)',
      }}>
        <div style={{ color: 'var(--accent)', fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.75rem' }}>
          {useCustom ? 'Custom Configuration' : selectedPreset ? `${PRESETS[selectedPreset].name} Configuration` : 'Pipeline Configuration'}
        </div>

        <div className="form-group">
          <label>Encoding Technique</label>
          <select
            value={encoding}
            onChange={(e) => {
              setEncoding(e.target.value);
              if (!useCustom) { setUseCustom(true); setSelectedPreset(null); }
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
            value={installer}
            onChange={(e) => {
              setInstaller(e.target.value);
              if (!useCustom) { setUseCustom(true); setSelectedPreset(null); }
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
            value={persistence}
            onChange={(e) => {
              setPersistence(e.target.value);
              if (!useCustom) { setUseCustom(true); setSelectedPreset(null); }
            }}
          >
            {PERSISTENCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        className="btn-generate"
        onClick={handleGenerate}
        disabled={generating || (!selectedPreset && !useCustom)}
        style={{ marginTop: '0.75rem' }}
      >
        {generating ? <><LoaderIcon size={14} /> Generating...</> : <><LayersIcon size={14} /> Generate Combined Payload</>}
      </button>

      {result && (
        <div style={{ marginTop: '1rem' }}>
          {result.stages.length > 0 && (
            <div className="info-box success" style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 600, fontSize: '0.8125rem', marginBottom: '0.375rem' }}>
                <CheckIcon size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
                Stages Applied
              </div>
              <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                {result.stages.map((stage, idx) => (
                  <span key={idx} className="tag success">
                    {idx + 1}. {stage}
                  </span>
                ))}
              </div>
            </div>
          )}

          {Object.keys(result.metadata).length > 0 && (
            <div className="stat-grid">
              {Object.entries(result.metadata).map(([key, value]) => (
                <div key={key} className="stat-card">
                  <div className="stat-label">{key.replace(/_/g, ' ')}</div>
                  <div className="stat-value" style={{ fontSize: '0.75rem' }}>{String(value)}</div>
                </div>
              ))}
            </div>
          )}

          {result.size && (
            <div className="info-box neutral" style={{ marginBottom: '0.75rem' }}>
              Payload Size: <strong style={{ color: 'var(--accent)' }}>{(result.size / 1024).toFixed(2)} KB</strong>
            </div>
          )}

          <div className="output-controls">
            <button className="btn-primary" onClick={handleCopy}>
              {copied ? <><CheckIcon size={14} /> Copied</> : <><CopyIcon size={14} /> Copy Payload</>}
            </button>
            <button className="btn-primary" onClick={handleDownload}>
              <DownloadIcon size={14} /> Download
            </button>
          </div>

          <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
            Output Preview (First 30 lines)
          </div>
          <div className="code-preview">
            {result.content
              .split('\n')
              .slice(0, 30)
              .map((line, idx) => (
                <div key={idx}>{line || ' '}</div>
              ))}
            {result.content.split('\n').length > 30 && (
              <div style={{ color: 'var(--text-muted)', opacity: 0.5, marginTop: '0.5rem' }}>
                ... ({result.content.split('\n').length - 30} more lines)
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
