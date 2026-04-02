import type { BGPDocument } from '../types/api'

interface Props {
  report: BGPDocument | null
}

export function ReportPanel({ report }: Props) {
  if (!report) return null

  const { sections } = report

  return (
    <div id="report-panel" className="report-panel">
      <h1>{report.title}</h1>
      <p className="report-ref">Reference: {report.reference}</p>

      {report.summary && (
        <section className="report-summary">
          <h2>Summary</h2>
          <p>{report.summary}</p>
        </section>
      )}

      <section>
        <h2>1. Development Details</h2>
        <table>
          <tbody>
            <tr><td>Generated</td><td>{sections.development_details.generated_at}</td></tr>
            <tr><td>Bounding box</td><td>{sections.development_details.coordinates.bbox_wgs84?.map((n: number) => n.toFixed(5)).join(', ')}</td></tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>2. Pre-Development Habitat Baseline</h2>
        <table>
          <thead>
            <tr>
              <th>Habitat Type</th><th>Area (ha)</th><th>Distinctiveness</th>
              <th>Condition</th><th>Strategic Significance</th><th>BNG Units</th>
            </tr>
          </thead>
          <tbody>
            {sections.pre_development_habitat.map((row, i) => (
              <tr key={i}>
                <td>{row.habitat_type}</td>
                <td>{row.area_ha.toFixed(4)}</td>
                <td>{row.distinctiveness}</td>
                <td>{row.condition}</td>
                <td>{row.strategic_significance}</td>
                <td>{row.units.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>3. Post-Development Habitat (After Road Construction)</h2>
        <table>
          <thead>
            <tr>
              <th>Habitat Type</th><th>Area (ha)</th><th>Distinctiveness</th>
              <th>Condition</th><th>Strategic Significance</th><th>BNG Units</th>
            </tr>
          </thead>
          <tbody>
            {sections.post_development_habitat.map((row, i) => (
              <tr key={i}>
                <td>{row.habitat_type}</td>
                <td>{row.area_ha.toFixed(4)}</td>
                <td>{row.distinctiveness}</td>
                <td>{row.condition}</td>
                <td>{row.strategic_significance}</td>
                <td>{row.units.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>4. Biodiversity Gain Metric</h2>
        <table>
          <tbody>
            <tr><td>Pre-development total units</td><td>{sections.biodiversity_gain_metric.total_pre_units.toFixed(2)}</td></tr>
            <tr><td>Post-development total units</td><td>{sections.biodiversity_gain_metric.total_post_units.toFixed(2)}</td></tr>
            <tr><td>Net change (units)</td><td>{sections.biodiversity_gain_metric.net_change_units.toFixed(2)}</td></tr>
            <tr><td>Net change (%)</td><td>{sections.biodiversity_gain_metric.net_change_percent.toFixed(1)}%</td></tr>
            <tr><td>Minimum 10% gain required</td><td>{sections.biodiversity_gain_metric.minimum_gain_required.toFixed(2)} units</td></tr>
            <tr><td>Gain deficit</td><td>{sections.biodiversity_gain_metric.gain_deficit.toFixed(2)} units</td></tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2>5. Constraints &amp; Flags</h2>
        <table>
          <tbody>
            <tr>
              <td>Off-site compensation required</td>
              <td>{sections.off_site_compensation_required ? 'Yes' : 'No'}</td>
            </tr>
            <tr>
              <td>SSSI consultation required</td>
              <td>{sections.sssi_consultation_required ? 'Yes — mandatory consultation needed' : 'No'}</td>
            </tr>
            <tr>
              <td>LNRS areas crossed</td>
              <td>{sections.lnrs_areas_crossed.length > 0 ? sections.lnrs_areas_crossed.join(', ') : 'None'}</td>
            </tr>
          </tbody>
        </table>
      </section>

      {sections.notes && (
        <section>
          <h2>6. Notes</h2>
          <p>{sections.notes}</p>
        </section>
      )}
    </div>
  )
}
