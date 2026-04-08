import { useEffect } from 'react'

interface Props {
  onInfoClick: () => void
}

export function Header({ onInfoClick }: Props) {
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js'
    script.type = 'text/javascript'
    script.setAttribute('data-name', 'bmc-button')
    script.setAttribute('data-slug', 'openskips')
    script.setAttribute('data-color', '#FFDD00')
    script.setAttribute('data-emoji', '')
    script.setAttribute('data-font', 'Cookie')
    script.setAttribute('data-text', 'Buy me a coffee')
    script.setAttribute('data-outline-color', '#000000')
    script.setAttribute('data-font-color', '#000000')
    script.setAttribute('data-coffee-color', '#ffffff')
    script.async = true
    document.head.appendChild(script)
    return () => {
      document.head.removeChild(script)
    }
  }, [])

  return (
    <header className="app-header">
      <div className="app-header-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#18E299" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>BNG Path Planner</span>
      </div>
      <div className="app-header-actions">
        <a
          href="https://www.buymeacoffee.com/openskips"
          target="_blank"
          rel="noopener noreferrer"
          className="bmc-button"
          aria-label="Buy me a coffee"
        >
          <img
            src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
            alt="Buy Me A Coffee"
            style={{ height: '32px', width: 'auto' }}
          />
        </a>
        <button className="app-header-info-btn" onClick={onInfoClick} aria-label="About this tool">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          About
        </button>
      </div>
    </header>
  )
}
