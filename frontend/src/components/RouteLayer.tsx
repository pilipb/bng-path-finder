import { Polyline, Tooltip } from 'react-leaflet'
import type { LineString } from 'geojson'
import type { RouteSegment } from '../types/api'
import { segmentColour, distinctivenessLabel, formatLength, formatBNG } from '../utils/geo'

interface Props {
  route: LineString
  segments: RouteSegment[]
}

export function RouteLayer({ route, segments }: Props) {
  // Build the full path as ordered lat/lng pairs from the GeoJSON LineString
  const fullPath = route.coordinates.map(([lng, lat]) => [lat, lng] as [number, number])

  // Map each segment to the slice of the full path it covers, using proximity to
  // segment start/end to find breakpoints. Fall back to straight line if needed.
  const segmentPaths = segments.map((seg) => {
    // Find the closest point in fullPath to seg.start and seg.end
    const startIdx = closestIndex(fullPath, seg.start as [number, number])
    const endIdx = closestIndex(fullPath, seg.end as [number, number])
    const lo = Math.min(startIdx, endIdx)
    const hi = Math.max(startIdx, endIdx)
    const slice = hi > lo ? fullPath.slice(lo, hi + 1) : [seg.start as [number, number], seg.end as [number, number]]
    return { seg, path: slice }
  })

  return (
    <>
      {segmentPaths.map(({ seg, path }) => (
        <Polyline
          key={seg.index}
          positions={path}
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

function closestIndex(path: [number, number][], target: [number, number]): number {
  let best = 0
  let bestDist = Infinity
  for (let i = 0; i < path.length; i++) {
    const dlat = path[i][0] - target[0]
    const dlng = path[i][1] - target[1]
    const d = dlat * dlat + dlng * dlng
    if (d < bestDist) {
      bestDist = d
      best = i
    }
  }
  return best
}
