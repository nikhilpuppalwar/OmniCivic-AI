import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import type { IncidentContext } from '../lib/api';
import { Check, FileCheck2 } from 'lucide-react';

interface ResolutionPanelProps {
  incident: IncidentContext;
  onRefresh: () => Promise<void>;
}

export default function ResolutionPanel({ incident, onRefresh }: ResolutionPanelProps) {
  const [images, setImages] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [notes, setNotes] = useState('');
  const [demoAttempt, setDemoAttempt] = useState(1);

  // Suggested values for the two-attempt demo beat
  // Attempt 1: Mismatched image (e.g. garbage photo for water leak)
  // Attempt 2: Correct image (resolved leak photo)
  const attemptSuggestions = [
    {
      attempt: 1,
      title: 'Attempt 1: Mismatched Photo',
      image: 'resolved_leak_wrong.jpg',
      label: 'resolved_leak_wrong.jpg (Mismatched Location)',
      notes: 'Submitting repair proof photo from the cleanup team.',
      lat: 19.0255, // Mismatched latitude
      lon: 72.8355, // Mismatched longitude
    },
    {
      attempt: 2,
      title: 'Attempt 2: Correct Evidence',
      image: 'resolved_leak_correct.jpg',
      label: 'resolved_leak_correct.jpg (Valid Location)',
      notes: 'Road surface completely repaired and dry. Pipe replaced.',
      lat: 19.1190, // Correct latitude matches INC-2026-001 (19.1190)
      lon: 72.8470, // Correct longitude matches INC-2026-001 (72.8470)
    }
  ];

  useEffect(() => {
    api.getSeedImages().then(res => {
      setImages(res.images || []);
    }).catch(console.error);
  }, []);

  const handleApplyPreset = (preset: typeof attemptSuggestions[0]) => {
    setSelectedImage(preset.image);
    setNotes(preset.notes);
  };

  const handleSubmit = async (preset?: typeof attemptSuggestions[0]) => {
    setSubmitting(true);
    try {
      const img = preset ? preset.image : selectedImage;
      const lat = preset ? preset.lat : 19.1190;
      const lon = preset ? preset.lon : 72.8470;
      const nts = preset ? preset.notes : notes;

      await api.submitResolution(incident.incident_id, {
        after_photo: img,
        after_latitude: lat,
        after_longitude: lon,
        notes: nts,
      });

      await onRefresh();
      
      // Auto trigger verification after submission for a smooth demo flow
      setVerifying(true);
      await api.verifyResolution(incident.incident_id);
      await onRefresh();

      if (demoAttempt === 1) {
        setDemoAttempt(2);
      }
    } catch (e) {
      console.error(e);
      alert('Error submitting resolution');
    } finally {
      setSubmitting(false);
      setVerifying(false);
    }
  };

  const getStatusBannerColor = (res: string) => {
    switch (res) {
      case 'RESOLUTION_VERIFIED': return 'rgba(16, 185, 129, 0.12)';
      case 'LOCATION_MISMATCH': return 'rgba(239, 68, 68, 0.12)';
      case 'POSSIBLE_FAILED_RESOLUTION': return 'rgba(245, 158, 11, 0.12)';
      default: return 'var(--bg-primary)';
    }
  };

  const getStatusBorderColor = (res: string) => {
    switch (res) {
      case 'RESOLUTION_VERIFIED': return 'var(--status-resolved)';
      case 'LOCATION_MISMATCH': return 'var(--status-critical)';
      case 'POSSIBLE_FAILED_RESOLUTION': return 'var(--status-high)';
      default: return 'var(--border-primary)';
    }
  };

  const getStatusBadgeClass = (res: string) => {
    switch (res) {
      case 'RESOLUTION_VERIFIED': return 'badge-resolved';
      case 'LOCATION_MISMATCH': return 'badge-critical';
      case 'POSSIBLE_FAILED_RESOLUTION': return 'badge-high';
      default: return 'badge-low';
    }
  };

  const resState = incident.resolution?.verification_result || 'PENDING';

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
        Resolution Verification
      </h3>

      {/* Verification Result Banner */}
      {incident.resolution?.after_photo && (
        <div style={{
          padding: 12,
          background: getStatusBannerColor(resState),
          border: `1px solid ${getStatusBorderColor(resState)}`,
          borderRadius: 6,
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className={`badge ${getStatusBadgeClass(resState)}`}>
              {resState.replace(/_/g, ' ')}
            </span>
            <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
              Confidence: {Math.round((incident.resolution.confidence || 0) * 100)}%
            </span>
          </div>
          <p style={{ fontSize: 11, color: 'var(--text-primary)', lineHeight: 1.4, margin: 0 }}>
            {incident.resolution.verification_details}
          </p>
        </div>
      )}

      {/* Demo helper options */}
      {resState !== 'RESOLUTION_VERIFIED' && (
        <div style={{
          background: 'var(--bg-primary)',
          border: '1px solid var(--border-primary)',
          padding: 10,
          borderRadius: 6,
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
        }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)' }}>
            DEMO PRESETS (TWO-ATTEMPT BEAT)
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {attemptSuggestions.map((preset) => (
              <button
                key={preset.attempt}
                className="btn btn-secondary"
                style={{
                  fontSize: 10,
                  padding: 8,
                  textAlign: 'left',
                  borderColor: demoAttempt === preset.attempt ? 'var(--accent-blue)' : 'var(--border-primary)',
                  background: demoAttempt === preset.attempt ? 'rgba(37, 99, 235, 0.04)' : 'transparent',
                }}
                onClick={() => handleApplyPreset(preset)}
              >
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{preset.title}</div>
                <div style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>{preset.image}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Form Submission */}
      {resState !== 'RESOLUTION_VERIFIED' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>
              Select Resolution Photo Evidence
            </label>
            <select
              className="input"
              value={selectedImage}
              onChange={(e) => setSelectedImage(e.target.value)}
            >
              <option value="">-- Choose image --</option>
              {images.map((img) => (
                <option key={img} value={img}>{img}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>
              Resolution Notes
            </label>
            <textarea
              className="input"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Describe repairs carried out..."
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={() => handleSubmit()}
            disabled={submitting || verifying || !selectedImage}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {submitting || verifying ? (
              <span className="spinner" />
            ) : (
              <>
                <FileCheck2 size={14} />
                Submit and Verify Resolution
              </>
            )}
          </button>
        </div>
      )}

      {resState === 'RESOLUTION_VERIFIED' && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px 12px',
          background: 'rgba(16, 185, 129, 0.04)',
          border: '1px dashed var(--status-resolved)',
          borderRadius: 6,
          textAlign: 'center',
          gap: 8,
        }}>
          <Check size={28} color="var(--status-resolved)" />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--status-resolved)' }}>
            Incident Resolved Successfully
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            Before/After photos verified. GPS proximity check passed.
          </span>
        </div>
      )}
    </div>
  );
}
