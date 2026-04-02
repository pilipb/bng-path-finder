export function segmentColour(distinctiveness: number, ancientWoodland: boolean): string {
  if (ancientWoodland) return '#1a1a1a'
  if (distinctiveness >= 8) return '#dc2626'   // red
  if (distinctiveness >= 6) return '#ea580c'   // orange
  if (distinctiveness >= 4) return '#ca8a04'   // amber
  if (distinctiveness >= 2) return '#65a30d'   // yellow-green
  return '#16a34a'                              // green
}

export function distinctivenessLabel(d: number): string {
  if (d >= 8) return 'Very High'
  if (d >= 6) return 'High'
  if (d >= 4) return 'Medium'
  if (d >= 2) return 'Low'
  return 'Very Low'
}

export function formatLength(m: number): string {
  if (m >= 1000) return `${(m / 1000).toFixed(2)} km`
  return `${Math.round(m)} m`
}

export function formatBNG(units: number): string {
  return units.toFixed(2)
}
