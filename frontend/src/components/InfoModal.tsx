interface Props {
  onClose: () => void
}

export function InfoModal({ onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box info-modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>About BNG Path Planner</h2>
          <p className="modal-subtitle">
            A decision-support tool for Biodiversity Net Gain route planning in England.
          </p>
        </div>

        <div className="modal-body info-modal-body">
          <section className="info-section">
            <h3>What is this tool?</h3>
            <p>
              BNG Path Planner helps developers, ecologists, and planners identify the most
              biodiversity-efficient route between two points on the map. Given a proposed
              development site (Point A) and an off-site habitat creation or enhancement
              location (Point B), the tool calculates the path that minimises ecological
              impact while maximising Biodiversity Net Gain unit delivery.
            </p>
          </section>

          <section className="info-section">
            <h3>How it works</h3>
            <ol className="info-list">
              <li>
                <strong>Place Point A</strong> — click the map to mark your development
                site or start location.
              </li>
              <li>
                <strong>Place Point B</strong> — click again to mark the habitat delivery
                or end location.
              </li>
              <li>
                <strong>Calculate route</strong> — the backend queries live spatial datasets
                (SSSIs, Local Nature Recovery Strategies, Ancient Woodland) to find the
                BNG-optimal path and estimate habitat unit costs per segment.
              </li>
              <li>
                <strong>Generate a Biodiversity Gain Plan</strong> — produce a draft BGP
                document summarising habitat baseline, BNG metric, and required gains, ready
                for planning submissions.
              </li>
            </ol>
          </section>

          <section className="info-section">
            <h3>Ecological constraints considered</h3>
            <ul className="info-list">
              <li><strong>SSSIs</strong> — Sites of Special Scientific Interest (high avoidance cost)</li>
              <li><strong>LNRS</strong> — Local Nature Recovery Strategy priority areas (moderate uplift)</li>
              <li><strong>Ancient Woodland</strong> — irreplaceable habitats flagged for maximum protection</li>
            </ul>
          </section>

          <section className="info-section">
            <h3>Important caveats</h3>
            <p>
              This tool is intended as a planning aid and does not substitute for a
              statutory Biodiversity Net Gain assessment, a qualified ecologist's survey,
              or formal planning advice. BNG unit calculations are indicative only and are
              based on simplified habitat classifications. Always verify outputs against
              current Natural England guidance and the statutory BNG metric.
            </p>
          </section>

          <section className="info-section info-section--last">
            <h3>Further reading</h3>
            <ul className="info-list">
              <li>
                <a href="https://www.gov.uk/guidance/biodiversity-net-gain" target="_blank" rel="noopener noreferrer">
                  GOV.UK — Biodiversity Net Gain guidance
                </a>
              </li>
              <li>
                <a href="https://naturalengland.blog.gov.uk/2023/11/14/biodiversity-net-gain-what-you-need-to-know/" target="_blank" rel="noopener noreferrer">
                  Natural England — BNG: what you need to know
                </a>
              </li>
              <li>
                <a href="https://www.gov.uk/guidance/local-nature-recovery-strategies" target="_blank" rel="noopener noreferrer">
                  GOV.UK — Local Nature Recovery Strategies
                </a>
              </li>
            </ul>
          </section>
        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" style={{ width: 'auto' }} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
