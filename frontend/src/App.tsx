import { useState, useCallback } from 'react'
import { MapView } from './components/MapView'
import { MarkerLayer } from './components/MarkerLayer'
import { RouteLayer } from './components/RouteLayer'
import { Sidebar } from './components/Sidebar'
import { ReportPanel } from './components/ReportPanel'
import { DeveloperDetailsModal } from './components/DeveloperDetailsModal'
import { Header } from './components/Header'
import { InfoModal } from './components/InfoModal'
import { useRoute } from './hooks/useRoute'
import { useReport } from './hooks/useReport'
import { useFormPdf } from './hooks/useFormPdf'
import { useResearch } from './hooks/useResearch'
import type { DeveloperDetails } from './types/api'
import './App.css'

type Step = 'place-a' | 'place-b' | 'ready' | 'loading' | 'done'

export default function App() {
  const [step, setStep] = useState<Step>('place-a')
  const [pointA, setPointA] = useState<[number, number] | null>(null)
  const [pointB, setPointB] = useState<[number, number] | null>(null)

  const route = useRoute()
  const report = useReport()
  const formPdf = useFormPdf()
  const research = useResearch(report.data, route.data)

  const [showFormModal, setShowFormModal] = useState(false)
  const [showInfo, setShowInfo] = useState(false)

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

  const handleDownloadOfficialForm = useCallback(async (details: DeveloperDetails) => {
    if (!route.data || !report.data) return
    await formPdf.downloadPdf({
      route_result: route.data,
      bgp_document: report.data,
      developer: details,
    })
    setShowFormModal(false)
  }, [route.data, report.data, formPdf])

  const handleReset = useCallback(() => {
    setPointA(null)
    setPointB(null)
    route.reset()
    report.reset()
    research.reset()
    setStep('place-a')
  }, [route, report, research])

  return (
    <>
      <div className="app-root">
      <Header onInfoClick={() => setShowInfo(true)} />
      <div className="app-layout">
        <div className="map-area">
          <MapView step={step} onMapClick={handleMapClick}>
            <MarkerLayer pointA={pointA} pointB={pointB} />
            {route.data && <RouteLayer route={route.data.route} segments={route.data.segments} />}
          </MapView>
        </div>
        <Sidebar
          step={step}
          pointA={pointA}
          pointB={pointB}
          routeResult={route.data}
          reportData={report.data}
          enrichedRecommendations={research.enriched}
          researchLoading={research.loading}
          error={route.error}
          onCalculate={handleCalculate}
          onGenerateReport={handleGenerateReport}
          onReset={handleReset}
          reportLoading={report.loading}
          onOpenFormModal={() => setShowFormModal(true)}
        />
      </div>
      </div>
      <ReportPanel report={report.data} />
      {showInfo && <InfoModal onClose={() => setShowInfo(false)} />}
      {showFormModal && (
        <DeveloperDetailsModal
          onSubmit={handleDownloadOfficialForm}
          onClose={() => setShowFormModal(false)}
          loading={formPdf.loading}
        />
      )}
    </>
  )
}
