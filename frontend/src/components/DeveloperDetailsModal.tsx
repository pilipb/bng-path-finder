import { useState } from 'react'
import type { DeveloperDetails } from '../types/api'

interface Props {
  onSubmit: (details: DeveloperDetails) => void
  onClose: () => void
  loading: boolean
}

const EMPTY: DeveloperDetails = {
  applicant_name: '',
  company_name: '',
  site_address: '',
  lpa: '',
  planning_app_ref: '',
  development_description: '',
  email: '',
  telephone: '',
}

export function DeveloperDetailsModal({ onSubmit, onClose, loading }: Props) {
  const [details, setDetails] = useState<DeveloperDetails>(EMPTY)

  function set(field: keyof DeveloperDetails, value: string) {
    setDetails(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="modal-overlay" onClick={loading ? undefined : onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>

        {/* Spinner overlay — shown while PDF is being generated */}
        {loading && (
          <div className="modal-loading-overlay">
            <div className="modal-spinner" />
            <p className="modal-loading-text">Generating your PDF…</p>
          </div>
        )}

        <div className="modal-header">
          <h2>Official BNG Form</h2>
          <div className="modal-autofill-note">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            This system will attempt to pre-fill as much of the official government form as possible using your route and report data. You can review and complete any remaining fields before submission.
          </div>
          <p className="modal-subtitle">
            Optionally enter your details below. All fields are optional — click "Skip" to download with blanks.
          </p>
        </div>

        <div className="modal-body">
          <div className="modal-field-grid">
            <label>Applicant name
              <input value={details.applicant_name} onChange={e => set('applicant_name', e.target.value)} placeholder="Full name" disabled={loading} />
            </label>
            <label>Company / organisation
              <input value={details.company_name} onChange={e => set('company_name', e.target.value)} placeholder="Company name" disabled={loading} />
            </label>
            <label>LPA (Local Planning Authority)
              <input value={details.lpa} onChange={e => set('lpa', e.target.value)} placeholder="e.g. Wiltshire Council" disabled={loading} />
            </label>
            <label>Planning application reference
              <input value={details.planning_app_ref} onChange={e => set('planning_app_ref', e.target.value)} placeholder="e.g. 24/01234/FUL" disabled={loading} />
            </label>
            <label>Site address
              <input value={details.site_address} onChange={e => set('site_address', e.target.value)} placeholder="Site address or grid reference" disabled={loading} />
            </label>
            <label>Email
              <input type="email" value={details.email} onChange={e => set('email', e.target.value)} placeholder="email@example.com" disabled={loading} />
            </label>
            <label>Telephone
              <input value={details.telephone} onChange={e => set('telephone', e.target.value)} placeholder="+44..." disabled={loading} />
            </label>
          </div>
          <label className="modal-full-width">Development description
            <textarea
              value={details.development_description}
              onChange={e => set('development_description', e.target.value)}
              placeholder="Describe the development (max 250 words)"
              rows={3}
              maxLength={1500}
              disabled={loading}
            />
          </label>
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={() => onSubmit(EMPTY)} disabled={loading}>
            Skip & Download
          </button>
          <button className="btn btn-primary" onClick={() => onSubmit(details)} disabled={loading}>
            Generate &amp; Download
          </button>
        </div>
      </div>
    </div>
  )
}
