import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet icon paths broken by Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

interface Props {
  step: 'place-a' | 'place-b' | 'ready' | 'loading' | 'done'
  onMapClick: (lat: number, lng: number) => void
  children?: React.ReactNode
}

function ClickHandler({ step, onMapClick }: { step: Props['step']; onMapClick: Props['onMapClick'] }) {
  useMapEvents({
    click(e) {
      if (step === 'place-a' || step === 'place-b' || step === 'done') {
        onMapClick(e.latlng.lat, e.latlng.lng)
      }
    },
  })
  return null
}

export function MapView({ step, onMapClick, children }: Props) {
  return (
    <MapContainer
      center={[52.5, -1.5]}
      zoom={7}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler step={step} onMapClick={onMapClick} />
      {children}
    </MapContainer>
  )
}
