import { Polyline, Tooltip } from 'react-leaflet'
import type { RouteSegment } from '../types/api'
import { segmentColour, distinctivenessLabel, formatLength, formatBNG } from '../utils/geo'

interface Props {
  segments: RouteSegment[]
}

export function RouteLayer({ segments }: Props) {
  return (
    <>
      {segments.map((seg) => (
        <Polyline
          key={seg.index}
          positions={[seg.start, seg.end]}
          pathOptions={{
            color: segmentColour(seg.distinctiveness, seg.ancient_woodland),
            weight: 5,
            opacity: 0.85,
          }}
        >
          <Tooltip sticky>
            <div style={{ fontSize: '13px', lineHeight: 1.5 }}>
              <strong>{seg.habitat_type}</strong><br />
              Distinctiveness: {seg.distinctiveness} — {distinctivenessLabel(seg.distinctiveness)}<br />
              Length: {formatLength(seg.length_m)}<br />
              BNG units: {formatBNG(seg.bng_units)}<br />
              {seg.sssi_flag && <span style={{ color: '#dc2626' }}>⚠ SSSI zone<br /></span>}
              {seg.lnrs_flag && <span style={{ color: '#b45309' }}>★ LNRS area (×1.15)<br /></span>}
              {seg.ancient_woodland && <span style={{ color: '#1a1a1a' }}>🚫 Ancient Woodland<br /></span>}
            </div>
          </Tooltip>
        </Polyline>
      ))}
    </>
  )
}
