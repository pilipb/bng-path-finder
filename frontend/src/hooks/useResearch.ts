import { useState, useEffect } from 'react'
import type { BGPDocument, RouteResponse, EnrichedRecommendation } from '../types/api'

export function useResearch(reportData: BGPDocument | null, routeResult: RouteResponse | null) {
  const [enriched, setEnriched] = useState<EnrichedRecommendation[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reportData || !routeResult) return
    // Only research if there are high-priority recommendations
    const hasHigh = reportData.recommendations?.some(r => r.priority === 'high')
    if (!hasHigh) return

    let cancelled = false
    setLoading(true)
    setEnriched(null)
    setError(null)

    fetch('/api/recommendations/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bgp_document: reportData, route_result: routeResult }),
    })
      .then(res => {
        if (!res.ok) throw new Error(`Research request failed: ${res.status}`)
        return res.json()
      })
      .then((json: { recommendations: EnrichedRecommendation[] }) => {
        if (!cancelled) setEnriched(json.recommendations)
      })
      .catch(e => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [reportData, routeResult])

  function reset() {
    setEnriched(null)
    setError(null)
    setLoading(false)
  }

  return { enriched, loading, error, reset }
}
