import type { BGPDocument, HabitatRow, Recommendation } from '../types/api'

interface Props {
  report: BGPDocument
}

function HabitatTable({ rows }: { rows: HabitatRow[] }) {
  return (
    <div className="rv-table-wrap">
      <table className="rv-table">
        <thead>
          <tr>
            <th>Habitat Type</th>
            <th>Area (ha)</th>
            <th>Distinct.</th>
            <th>Condition</th>
            <th>Strat. Sig.</th>
            <th>Units</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              <td>{row.habitat_type}</td>
              <td>{row.area_ha.toFixed(4)}</td>
              <td>{row.distinctiveness}</td>
              <td>{row.condition}</td>
              <td>{row.strategic_significance}</td>
              <td>{row.units.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const PRIORITY_CONFIG = {
  high:   { label: 'Action required', className: 'rec-priority-high' },
  medium: { label: 'Required before submission', className: 'rec-priority-medium' },
  low:    { label: 'Recommended', className: 'rec-priority-low' },
}

function NextSteps({ recommendations }: { recommendations: Recommendation[] }) {
  if (!recommendations?.length) return null
  return (
    <div className="rv-section rv-next-steps">
      <div className="rv-section-label">Next Steps &amp; Recommendations</div>
      <p className="rv-next-steps-intro">
        The following actions are required or recommended before this plan can be formally submitted.
        Items marked <strong>Action required</strong> must be resolved.
      </p>
      <div className="rv-rec-list">
        {recommendations.map((rec, i) => {
          const cfg = PRIORITY_CONFIG[rec.priority] ?? PRIORITY_CONFIG.low
          return (
            <div key={i} className={`rv-rec-card ${cfg.className}`}>
              <div className="rv-rec-header">
                <span className="rv-rec-badge">{cfg.label}</span>
                <span className="rv-rec-title">{rec.title}</span>
              </div>
              <p className="rv-rec-detail">{rec.detail}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function ReportView({ report }: Props) {
  const { sections } = report
  const metric = sections.biodiversity_gain_metric
  const hasDeficit = metric.gain_deficit > 0
  const coords = sections.development_details.coordinates

  return (
    <div className="report-view">
      {/* Header */}
      <div className="rv-header">
        <div className="rv-title">Biodiversity Gain Plan</div>
        <div className="rv-ref">{report.reference}</div>
      </div>

      {/* Plain-English summary */}
      {report.summary && (
        <div className="rv-summary-card">
          <div className="rv-summary-label">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Plain-English Summary
          </div>
          <p className="rv-summary-text">{report.summary}</p>
        </div>
      )}

      {/* Development details */}
      <div className="rv-section">
        <div className="rv-section-label">Development Details</div>
        <div className="rv-kv-grid">
          <span className="rv-key">Generated</span>
          <span className="rv-val">{new Date(sections.development_details.generated_at).toLocaleString()}</span>
          {coords.bbox_wgs84 && (
            <>
              <span className="rv-key">Area bbox</span>
              <span className="rv-val rv-mono">{(coords.bbox_wgs84 as number[]).map((n: number) => n.toFixed(4)).join(', ')}</span>
            </>
          )}
        </div>
      </div>

      {/* Summary metric card */}
      <div className={`rv-metric-card ${hasDeficit ? 'rv-metric-deficit' : 'rv-metric-gain'}`}>
        <div className="rv-metric-title">Biodiversity Gain Metric</div>
        <div className="rv-metric-grid">
          <div className="rv-metric-item">
            <span className="rv-metric-label">Pre-dev units</span>
            <span className="rv-metric-value">{metric.total_pre_units.toFixed(2)}</span>
          </div>
          <div className="rv-metric-item">
            <span className="rv-metric-label">Post-dev units</span>
            <span className="rv-metric-value">{metric.total_post_units.toFixed(2)}</span>
          </div>
          <div className="rv-metric-item">
            <span className="rv-metric-label">Net change</span>
            <span className="rv-metric-value">{metric.net_change_percent.toFixed(1)}%</span>
          </div>
          <div className="rv-metric-item">
            <span className="rv-metric-label">Gain deficit</span>
            <span className="rv-metric-value">{metric.gain_deficit.toFixed(2)}</span>
          </div>
        </div>
        <div className={`rv-offsite-badge ${hasDeficit ? 'rv-badge-red' : 'rv-badge-green'}`}>
          {hasDeficit
            ? `Off-site compensation required — deficit: ${metric.gain_deficit.toFixed(2)} units`
            : 'No off-site compensation required'}
        </div>
      </div>

      {/* Pre-development habitat */}
      <div className="rv-section">
        <div className="rv-section-label">Pre-Development Habitat Baseline</div>
        <HabitatTable rows={sections.pre_development_habitat} />
      </div>

      {/* Post-development habitat */}
      <div className="rv-section">
        <div className="rv-section-label">Post-Development Habitat</div>
        <HabitatTable rows={sections.post_development_habitat} />
      </div>

      {/* Constraints */}
      <div className="rv-section">
        <div className="rv-section-label">Constraints &amp; Flags</div>
        {sections.sssi_consultation_required && (
          <div className="rv-flag rv-flag-sssi">
            SSSI consultation required — mandatory consultation needed
          </div>
        )}
        {sections.lnrs_areas_crossed.length > 0 && (
          <div className="rv-flag rv-flag-lnrs">
            LNRS areas crossed: {sections.lnrs_areas_crossed.join(', ')}
          </div>
        )}
        {!sections.sssi_consultation_required && sections.lnrs_areas_crossed.length === 0 && (
          <p className="rv-none">No significant constraints identified.</p>
        )}
      </div>

      {/* Notes */}
      {sections.notes && (
        <div className="rv-section">
          <div className="rv-section-label">Notes</div>
          <p className="rv-notes">{sections.notes}</p>
        </div>
      )}

      {/* Next steps */}
      <NextSteps recommendations={report.recommendations} />
    </div>
  )
}
