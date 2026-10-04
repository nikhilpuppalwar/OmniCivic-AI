import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { CivicReport, IncidentContext, SensitiveSite } from '../lib/api';
import { useTheme } from '../context/ThemeContext';


// Default Mumbai City Center coordinates for fallback
const DEFAULT_CENTER: [number, number] = [19.1136, 72.8697];

// Priority Color Tokens matching CSS theme
const PRIORITY_COLORS: Record<string, string> = {
  CRITICAL: '#EF4444',
  HIGH: '#F59E0B',
  MEDIUM: '#3B82F6',
  LOW: '#64748B',
  RESOLVED: '#10B981',
};

export interface MapViewProps {
  reports?: CivicReport[];
  incidents?: IncidentContext[];
  selectedReportId?: string | null;
  selectedIncidentId?: string | null;
  onSelectReport?: (reportId: string) => void;
  onSelectIncident?: (incidentId: string) => void;
  height?: string;
  className?: string;
  compact?: boolean;
}

// Subcomponent to smoothly animate map center on selection changes
function RecenterMap({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true, duration: 0.8 });
  }, [map, center, zoom]);
  return null;
}

// Subcomponent to ensure map recalculates tile bounds on tab/container resize
function MapResizer() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 150);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}


// Create custom colored HTML DivIcons for crisp styling in dark mode
function createReportIcon(color: string, isSelected: boolean) {
  return L.divIcon({
    className: 'custom-report-pin',
    html: `
      <div style="
        position: relative;
        width: ${isSelected ? '24px' : '18px'};
        height: ${isSelected ? '24px' : '18px'};
        background-color: ${color};
        border: 2px solid #ffffff;
        border-radius: 50%;
        box-shadow: 0 0 ${isSelected ? '12px' : '6px'} ${color};
        cursor: pointer;
        transition: all 0.2s ease;
      ">
        ${isSelected ? `<div style="
          position: absolute;
          inset: -6px;
          border-radius: 50%;
          border: 2px solid ${color};
          animation: pulse-dot 1.5s infinite;
        "></div>` : ''}
      </div>
    `,
    iconSize: [isSelected ? 24 : 18, isSelected ? 24 : 18],
    iconAnchor: [isSelected ? 12 : 9, isSelected ? 12 : 9],
  });
}

// Custom icon for Sensitive Sites (schools, hospitals, clinics)
function createSensitiveSiteIcon(type: string) {
  const iconSymbol = type.includes('hospital') || type.includes('clinic') ? '🏥' : '🏫';
  return L.divIcon({
    className: 'custom-sensitive-pin',
    html: `
      <div style="
        font-size: 16px;
        background: #1E2A3A;
        border: 1px solid #3B82F6;
        border-radius: 6px;
        padding: 2px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        ${iconSymbol}
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });
}

export const MapView: React.FC<MapViewProps> = ({
  reports = [],
  incidents = [],
  selectedReportId,
  selectedIncidentId,
  onSelectReport,
  onSelectIncident,
  height = '500px',
  className = '',
  compact = false,
}) => {
  // Determine center coordinates and zoom based on selection
  let mapCenter: [number, number] = DEFAULT_CENTER;
  let mapZoom = compact ? 15 : 13;

  if (selectedIncidentId) {
    const foundInc = incidents.find((i) => i.incident_id === selectedIncidentId);
    if (foundInc && foundInc.cluster) {
      mapCenter = [foundInc.cluster.center_lat, foundInc.cluster.center_lon];
      mapZoom = 16;
    }
  } else if (selectedReportId) {
    const foundRep = reports.find((r) => r.report_id === selectedReportId);
    if (foundRep && foundRep.location) {
      mapCenter = [foundRep.location.latitude, foundRep.location.longitude];
      mapZoom = 16;
    }
  } else if (reports.length > 0 && reports[0].location) {
    mapCenter = [reports[0].location.latitude, reports[0].location.longitude];
  }

  // Collect sensitive sites across selected or all incidents
  const displaySensitiveSites: SensitiveSite[] = [];
  const incidentsToProcess = selectedIncidentId
    ? incidents.filter((i) => i.incident_id === selectedIncidentId)
    : incidents;

  incidentsToProcess.forEach((inc) => {
    const sites = inc.nearby_sites || inc.root_cause?.nearby_sites || [];
    sites.forEach((site) => {
      const lat = site.latitude ?? site.lat;
      const lon = site.longitude ?? site.lon;
      if (lat !== undefined && lon !== undefined) {
        displaySensitiveSites.push({ ...site, latitude: lat, longitude: lon });
      }
    });
  });

  const { theme } = useTheme();

  // Dynamic Tile URL based on Active Theme — no API key required
  const tileUrl = theme === 'light'
    ? 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    : 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png';

  return (
    <div
      className={`relative rounded-xl overflow-hidden border border-[var(--border-primary)] shadow-xl bg-[var(--bg-secondary)] ${className}`}
      style={{ height }}
    >
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ width: '100%', height: '100%', background: 'var(--bg-primary)' }}
        zoomControl={!compact}
      >
        <RecenterMap center={mapCenter} zoom={mapZoom} />
        <MapResizer />

        {/* Theme-Adaptive tile layer — no API key required */}
        <TileLayer
          key={theme}
          url={tileUrl}
          maxZoom={19}
          attribution={
            theme === 'light'
              ? '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              : '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          }
        />




        {/* Render Incident Cluster Radius Circles */}
        {incidents.map((inc) => {
          if (!inc.cluster?.center_lat || !inc.cluster?.center_lon) return null;
          const isSelected = inc.incident_id === selectedIncidentId;
          const priority = inc.impact_score?.priority || 'HIGH';
          const color = PRIORITY_COLORS[priority] || '#3B82F6';

          return (
            <Circle
              key={inc.incident_id}
              center={[inc.cluster.center_lat, inc.cluster.center_lon]}
              radius={inc.cluster.radius_m || 180}
              pathOptions={{
                color: color,
                fillColor: color,
                fillOpacity: isSelected ? 0.25 : 0.1,
                weight: isSelected ? 2 : 1,
                dashArray: isSelected ? '4 4' : undefined,
              }}
              eventHandlers={{
                click: () => onSelectIncident?.(inc.incident_id),
              }}
            >
              <Popup>
                <div className="p-1 min-w-[200px] text-xs">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-mono font-bold text-blue-400">{inc.incident_id}</span>
                    <span
                      className="px-1.5 py-0.5 rounded text-[10px] font-bold"
                      style={{ backgroundColor: `${color}22`, color: color }}
                    >
                      {priority}
                    </span>
                  </div>
                  <div className="text-[var(--text-primary)] font-medium mb-1">
                    {inc.classification?.replace(/_/g, ' ')}
                  </div>
                  <div className="text-[var(--text-secondary)] mb-2">
                    Reports in cluster: {inc.cluster.report_count || inc.connected_reports.length}
                  </div>
                  {onSelectIncident && (
                    <button
                      onClick={() => onSelectIncident(inc.incident_id)}
                      className="w-full py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-medium cursor-pointer transition"
                    >
                      Focus Incident
                    </button>
                  )}
                </div>
              </Popup>
            </Circle>
          );
        })}

        {/* Render Citizen Report Pins */}
        {reports.map((r) => {
          if (!r.location?.latitude || !r.location?.longitude) return null;
          const isSelected = r.report_id === selectedReportId;
          const color = isSelected
            ? '#2563EB'
            : r.status === 'RESOLVED'
            ? '#10B981'
            : '#3B82F6';

          return (
            <Marker
              key={r.report_id}
              position={[r.location.latitude, r.location.longitude]}
              icon={createReportIcon(color, isSelected)}
              eventHandlers={{
                click: () => onSelectReport?.(r.report_id),
              }}
            >
              <Popup>
                <div className="p-1 min-w-[220px] text-xs">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-mono font-bold text-cyan-400">{r.report_id}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                      {r.ward || 'Ward'}
                    </span>
                  </div>
                  <div className="text-[var(--text-primary)] font-medium line-clamp-2 mb-2">
                    {r.description}
                  </div>
                  <div className="text-[var(--text-tertiary)] text-[10px] mb-2">
                    📍 {r.location.address || `${r.location.latitude}, ${r.location.longitude}`}
                  </div>
                  {onSelectReport && (
                    <button
                      onClick={() => onSelectReport(r.report_id)}
                      className="w-full py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs font-medium cursor-pointer transition"
                    >
                      Select Report
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Render Sensitive Site Pins (Schools, Hospitals, Clinics) */}
        {displaySensitiveSites.map((site, idx) => {
          const lat = site.latitude!;
          const lon = site.longitude!;
          return (
            <Marker
              key={site.id || `site-${idx}`}
              position={[lat, lon]}
              icon={createSensitiveSiteIcon(site.type)}
            >
              <Popup>
                <div className="p-1 text-xs">
                  <div className="font-semibold text-amber-400 mb-0.5">
                    {site.name}
                  </div>
                  <div className="text-slate-400 text-[10px] capitalize mb-1">
                    Type: {site.type} {site.distance_m ? `(${site.distance_m}m away)` : ''}
                  </div>
                  <div className="text-[10px] text-emerald-400">
                    Verified Sensitive Infrastructure
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Render Resolution Verification Polyline (Before/After GPS verification) */}
        {incidents.map((inc) => {
          if (!inc.resolution?.after_photo) return null;
          const report = reports.find((r) => inc.connected_reports.includes(r.report_id));
          if (!report?.location) return null;

          const beforeLoc: [number, number] = [report.location.latitude, report.location.longitude];
          // If resolution details contain coordinates or verification details
          const isMismatch = inc.resolution.verification_result === 'LOCATION_MISMATCH';
          const strokeColor = isMismatch ? '#EF4444' : '#10B981';

          return (
            <React.Fragment key={`verification-${inc.incident_id}`}>
              <Marker position={beforeLoc} icon={createReportIcon(strokeColor, false)}>
                <Popup>
                  <div className="p-1 text-xs">
                    <span className="font-bold text-emerald-400">Verification Point</span>
                    <div>Incident: {inc.incident_id}</div>
                    <div>Result: {inc.resolution.verification_result}</div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Sleek Theme-Adaptive Overlay Header / Legend */}
      <div
        className="absolute bottom-3 left-3 z-[1000] rounded-lg p-2 text-[11px] flex items-center gap-3 shadow-lg"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-primary)',
          color: 'var(--text-primary)',
          backdropFilter: 'blur(8px)',
        }}
      >

        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span>
          <span>Critical</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>
          <span>High</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block"></span>
          <span>Medium</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-sm">🏫</span>
          <span>Sensitive Site</span>
        </div>
      </div>
    </div>
  );
};

export default MapView;
