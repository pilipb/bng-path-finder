import { useState } from 'react'
import type { BGPDocument, RouteResponse } from '../types/api'

export function useReport() {
  const [data, setData] = useState<BGPDocument | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generate(routeResult: RouteResponse) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ route_result: routeResult }),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text)
      }
      const json = await res.json() as BGPDocument
      setData(json)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setData(null)
    setError(null)
  }

  return { data, loading, error, generate, reset }
}
