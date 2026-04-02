import { useState } from 'react'
import type { FormPdfRequest } from '../types/api'

export function useFormPdf() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function downloadPdf(req: FormPdfRequest): Promise<void> {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/form/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text)
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'bng_gain_plan_official.pdf'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return { downloadPdf, loading, error }
}
