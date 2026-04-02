import { useState, useEffect } from 'react'
import type { RouteResponse, BGPDocument } from '../types/api'
import { CostBreakdown } from './CostBreakdown'
import { ReportView } from './ReportView'
import { triggerPrint } from '../utils/print'

type Step = 'place-a' | 'place-b' | 'ready' | 'loading' | 'done'
type View = 'route' | 'report'

interface Props {
  step: Step
  pointA: [number, number] | null
  pointB: [number, number] | null
  routeResult: RouteResponse | null
  reportData: BGPDocument | null
  error: string | null
  onCalculate: () => void
  onGenerateReport: () => void
  onReset: () => void
  reportLoading: boolean
  onOpenFormModal: () => void
}

export function Sidebar({
  step, pointA, pointB, routeResult, reportData, error,
  onCalculate, onGenerateReport, onReset, reportLoading, onOpenFormModal,
}: Props) {
  const [view, setView] = useState<View>('route')

  // Switch to report view automatically when report data arrives
  useEffect(() => {
    if (reportData) {
      setView('report')
    }
  }, [reportData])

  // Reset to route view when the user resets the whole app
  useEffect(() => {
    if (step === 'place-a') {
      setView('route')
    }
  }, [step])

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>BNG Path Finder</h1>
        <p className="sidebar-subtitle">Biodiversity Net Gain route optimiser</p>
      </div>

      <div className="sidebar-content">
        {step === 'place-a' && (
          <div className="step-instruction">
            <div className="step-number">1</div>
            <p>Click the map to set <strong>Point A</strong> (route start)</p>
          </div>
        )}

        {step === 'place-b' && (
          <div className="step-instruction">
            <div className="step-number">2</div>
            <p>Point A set at {pointA?.[0].toFixed(5)}, {pointA?.[1].toFixed(5)}</p>
            <p>Click the map to set <strong>Point B</strong> (route end)</p>
          </div>
        )}

        {step === 'ready' && (
          <div className="step-ready">
            <div className="point-summary">
              <div>A: {pointA?.[0].toFixed(5)}, {pointA?.[1].toFixed(5)}</div>
              <div>B: {pointB?.[0].toFixed(5)}, {pointB?.[1].toFixed(5)}</div>
            </div>
            <button className="btn btn-primary" onClick={onCalculate}>
              Calculate BNG-Optimal Route
            </button>
            <button className="btn btn-ghost" onClick={onReset}>Reset</button>
          </div>
        )}

        {step === 'loading' && (
          <div className="step-loading">
            <div className="spinner" />
            <p>Fetching habitat data and calculating BNG-optimal route…</p>
          </div>
        )}

        {error && (
          <div className="error-banner">{error}</div>
        )}

        {step === 'done' && routeResult && (
          <div className="step-done">
            {/* Report view */}
            {view === 'report' && reportData && (
              <>
                <div className="rv-nav">
                  <button className="btn btn-ghost rv-back-btn" onClick={() => setView('route')}>
                    ← Back to Route
                  </button>
                  <button className="btn btn-secondary rv-print-btn" onClick={triggerPrint}>
                    Print Report
                  </button>
                  <button className="btn btn-secondary" onClick={onOpenFormModal}>
                    Fill out Biodiversity Gain Plan (PDF)
                  </button>
                </div>
                <ReportView report={reportData} />
                <div className="action-buttons">
                  <button className="btn btn-ghost" onClick={onReset}>Reset</button>
                </div>
              </>
            )}

            {/* Route / cost breakdown view */}
            {view === 'route' && (
              <>
                <CostBreakdown
                  segments={routeResult.segments}
                  totalBngUnits={routeResult.total_bng_units}
                  totalLengthM={routeResult.total_length_m}
                  cellSizeM={routeResult.cell_size_m}
                />
                <div className="action-buttons">
                  {!reportData && (
                    <button
                      className="btn btn-primary"
                      onClick={onGenerateReport}
                      disabled={reportLoading}
                    >
                      {reportLoading ? 'Generating…' : 'Generate Biodiversity Gain Plan'}
                    </button>
                  )}
                  {reportData && (
                    <button className="btn btn-secondary" onClick={() => setView('report')}>
                      View Report
                    </button>
                  )}
                  <button className="btn btn-ghost" onClick={onReset}>Reset</button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
