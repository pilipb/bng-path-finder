import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

interface Props {
  pointA: [number, number] | null
  pointB: [number, number] | null
}

const greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

export function MarkerLayer({ pointA, pointB }: Props) {
  return (
    <>
      {pointA && (
        <Marker position={pointA} icon={greenIcon}>
          <Popup>Point A (Start)</Popup>
        </Marker>
      )}
      {pointB && (
        <Marker position={pointB} icon={redIcon}>
          <Popup>Point B (End)</Popup>
        </Marker>
      )}
    </>
  )
}
