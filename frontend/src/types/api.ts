import type { LineString } from 'geojson'

export interface RouteRequest {
  point_a: [number, number]  // [lat, lng]
  point_b: [number, number]  // [lat, lng]
}

export interface RouteSegment {
  index: number
  start: [number, number]
  end: [number, number]
  length_m: number
  habitat_type: string
  distinctiveness: number
  bng_units: number
  sssi_flag: boolean
  lnrs_flag: boolean
  ancient_woodland: boolean
}

export interface RouteResponse {
  route: LineString
  segments: RouteSegment[]
  total_bng_units: number
  total_length_m: number
  cell_size_m: number
  bbox_wgs84: [number, number, number, number]
}

export interface HabitatRow {
  habitat_type: string
  area_ha: number
  distinctiveness: number
  condition: string
  strategic_significance: string
  units: number
}

export interface BiodiversityGainMetric {
  total_pre_units: number
  total_post_units: number
  net_change_units: number
  net_change_percent: number
  minimum_gain_required: number
  gain_deficit: number
}

export interface BGPSections {
  development_details: { generated_at: string; coordinates: { bbox_wgs84?: number[] } }
  pre_development_habitat: HabitatRow[]
  post_development_habitat: HabitatRow[]
  biodiversity_gain_metric: BiodiversityGainMetric
  off_site_compensation_required: boolean
  sssi_consultation_required: boolean
  lnrs_areas_crossed: string[]
  notes: string
}

export interface Recommendation {
  priority: 'high' | 'medium' | 'low'
  title: string
  detail: string
}

export interface ResearchLink {
  title: string
  url: string
  description: string
}

export interface EnrichedRecommendation extends Recommendation {
  links: ResearchLink[]
  guidance: string
  timeline: string | null
  researched: boolean
}

export interface BGPDocument {
  title: string
  reference: string
  summary: string
  sections: BGPSections
  recommendations: Recommendation[]
}

export interface ReportRequest {
  route_result: RouteResponse
}

export interface DeveloperDetails {
  applicant_name: string
  company_name: string
  site_address: string
  lpa: string
  planning_app_ref: string
  development_description: string
  email: string
  telephone: string
}

export interface FormPdfRequest {
  route_result: RouteResponse
  bgp_document: BGPDocument
  developer: DeveloperDetails
}
