import { useState, useCallback } from 'react'
import { MapView } from './components/MapView'
import { MarkerLayer } from './components/MarkerLayer'
import { RouteLayer } from './components/RouteLayer'
import { Sidebar } from './components/Sidebar'
import { ReportPanel } from './components/ReportPanel'
import { useRoute } from './hooks/useRoute'
import { useReport } from './hooks/useReport'
import './App.css'

type Step = 'place-a' | 'place-b' | 'ready' | 'loading' | 'done'

export default function App() {
  const [step, setStep] = useState<Step>('place-a')
  const [pointA, setPointA] = useState<[number, number] | null>(null)
  const [pointB, setPointB] = useState<[number, number] | null>(null)

  const route = useRoute()
  const report = useReport()

  const handleMapClick = useCallback((lat: number, lng: number) => {
    if (step === 'place-a') {
      setPointA([lat, lng])
      setStep('place-b')
    } else if (step === 'place-b') {
      setPointB([lat, lng])
      setStep('ready')
    } else if (step === 'done') {
      // Reset and start over
      setPointA([lat, lng])
      setPointB(null)
      route.reset()
      report.reset()
      setStep('place-b')
    }
  }, [step, route, report])

  const handleCalculate = useCallback(async () => {
    if (!pointA || !pointB) return
    setStep('loading')
    await route.calculate({ point_a: pointA, point_b: pointB })
    setStep('done')
  }, [pointA, pointB, route])

  const handleGenerateReport = useCallback(async () => {
    if (!route.data) return
    await report.generate(route.data)
  }, [route.data, report])

  const handleReset = useCallback(() => {
    setPointA(null)
    setPointB(null)
    route.reset()
    report.reset()
    setStep('place-a')
  }, [route, report])

  return (
    <>
      <div className="app-layout">
        <div className="map-area">
          <MapView step={step} onMapClick={handleMapClick}>
            <MarkerLayer pointA={pointA} pointB={pointB} />
            {route.data && <RouteLayer segments={route.data.segments} />}
          </MapView>
        </div>
        <Sidebar
          step={step}
          pointA={pointA}
          pointB={pointB}
          routeResult={route.data}
          reportData={report.data}
          error={route.error}
          onCalculate={handleCalculate}
          onGenerateReport={handleGenerateReport}
          onReset={handleReset}
          reportLoading={report.loading}
        />
      </div>
      <ReportPanel report={report.data} />
    </>
  )
}
