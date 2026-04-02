import type { RouteSegment } from '../types/api'
import { segmentColour, distinctivenessLabel, formatLength, formatBNG } from '../utils/geo'

interface Props {
  segments: RouteSegment[]
  totalBngUnits: number
  totalLengthM: number
  cellSizeM: number
}

export function CostBreakdown({ segments, totalBngUnits, totalLengthM, cellSizeM }: Props) {
  const hasSSsi = segments.some((s) => s.sssi_flag)
  const hasLnrs = segments.some((s) => s.lnrs_flag)
  const hasAW = segments.some((s) => s.ancient_woodland)

  return (
    <div className="cost-breakdown">
      <div className="summary-stats">
        <div className="stat">
          <span className="stat-label">Total BNG impact</span>
          <span className="stat-value">{formatBNG(totalBngUnits)} units</span>
        </div>
        <div className="stat">
          <span className="stat-label">Route length</span>
          <span className="stat-value">{formatLength(totalLengthM)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Grid resolution</span>
          <span className="stat-value">{cellSizeM}m</span>
        </div>
      </div>

      {hasSSsi && (
        <div className="flag-banner flag-sssi">
          ⚠ SSSI consultation required — route passes through an SSSI Impact Risk Zone
        </div>
      )}
      {hasLnrs && (
        <div className="flag-banner flag-lnrs">
          ★ Route passes through LNRS Strategic Significance area — unit values ×1.15
        </div>
      )}
      {hasAW && (
        <div className="flag-banner flag-aw">
          🚫 Route passes through Ancient Woodland — this section may be impassable
        </div>
      )}

      <div className="segment-table-wrapper">
        <table className="segment-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Habitat Type</th>
              <th>Distinctiveness</th>
              <th>Length</th>
              <th>BNG Units</th>
              <th>Flags</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((seg) => (
              <tr
                key={seg.index}
                style={{
                  borderLeft: `4px solid ${segmentColour(seg.distinctiveness, seg.ancient_woodland)}`,
                }}
              >
                <td>{seg.index + 1}</td>
                <td>{seg.habitat_type}</td>
                <td>{seg.distinctiveness} — {distinctivenessLabel(seg.distinctiveness)}</td>
                <td>{formatLength(seg.length_m)}</td>
                <td>{formatBNG(seg.bng_units)}</td>
                <td>
                  {seg.sssi_flag && <span className="pill pill-sssi">SSSI</span>}
                  {seg.lnrs_flag && <span className="pill pill-lnrs">LNRS</span>}
                  {seg.ancient_woodland && <span className="pill pill-aw">NO-GO</span>}
                  {!seg.sssi_flag && !seg.lnrs_flag && !seg.ancient_woodland && '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
