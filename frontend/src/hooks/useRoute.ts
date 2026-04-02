import { useState } from 'react'
import type { RouteRequest, RouteResponse } from '../types/api'

export function useRoute() {
  const [data, setData] = useState<RouteResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function calculate(req: RouteRequest) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text)
      }
      const json = await res.json() as RouteResponse
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

  return { data, loading, error, calculate, reset }
}
