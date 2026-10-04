import { useState, useEffect, useRef } from 'react';
import { api, API_BASE } from '../lib/api';
import type { GeocodeResult } from '../lib/api';
import { 
  Landmark, 
  FilePlus, 
  ClipboardCheck, 
  ArrowRight, 
  UploadCloud, 
  Compass, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2,
  Search,
  X,
  Loader2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';


type InputMode = 'UPLOAD' | 'DEMO';
type LocationStatus = 'idle' | 'detecting' | 'success' | 'denied';

export default function CitizenReport() {
  const navigate = useNavigate();
  const [inputMode, setInputMode] = useState<InputMode>('UPLOAD');
  
  // Demo Mode States
  const [images, setImages] = useState<string[]>([]);
  const [selectedDemoImage, setSelectedDemoImage] = useState('');
  
  // Upload Mode States
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  // Common Report States
  const [citizenName, setCitizenName] = useState('Anonymous');
  const [phone, setPhone] = useState('+91-98200-11111');
  const [description, setDescription] = useState('');
  
  // Location States (explicit for Upload mode)
  const [locationName, setLocationName] = useState('');
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const [locationStatus, setLocationStatus] = useState<LocationStatus>('idle');

  // Address Search & Geocoding States (Task 8: OSM Nominatim Proxy)
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<GeocodeResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  
  const mapRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  const [submitting, setSubmitting] = useState(false);
  const [submittedReport, setSubmittedReport] = useState<any>(null);

  // Default coordinate presets corresponding to seed images for reliable demo clustering
  const PRESET_COORDS: Record<string, { lat: number; lon: number; addr: string; ward: string; desc: string }> = {
    'leak_01.jpg': {
      lat: 19.1190,
      lon: 72.8470,
      addr: 'Near Chakala Junction, Andheri East',
      ward: 'Ward 7 - Andheri East',
      desc: 'Major underground pipe leak. Water gushing onto the road causing erosion.',
    },
    'road_damage_01.jpg': {
      lat: 19.1192,
      lon: 72.8472,
      addr: 'Chakala Junction Main Road, Andheri East',
      ward: 'Ward 7 - Andheri East',
      desc: 'Cracked asphalt base near Chakala. Road surface crumbling.',
    },
    'pothole_01.jpg': {
      lat: 19.1188,
      lon: 72.8468,
      addr: 'Opposite Star Mall, Andheri East',
      ward: 'Ward 7 - Andheri East',
      desc: 'Deep pothole filled with muddy water. Hazardous for vehicles.',
    },
    'waterlogging_01.jpg': {
      lat: 19.1191,
      lon: 72.8469,
      addr: 'Chakala Signal Road, Andheri East',
      ward: 'Ward 7 - Andheri East',
      desc: 'Flooded road section near Chakala. Water accumulating post-rain.',
    },
    'exposed_wire_01.jpg': {
      lat: 19.0760,
      lon: 72.8780,
      addr: 'Near St. Xavier\'s School Gate, Marine Lines',
      ward: 'Ward 3 - Marine Lines',
      desc: 'Exposed electrical wires hanging low. Extremely hazardous.',
    },
    'garbage_01.jpg': {
      lat: 19.0719,
      lon: 72.8558,
      addr: 'Tilak Nagar Colony, Kurla',
      ward: 'Ward 6 - Kurla',
      desc: 'Waste bins overflowing. Debris scattered into drainage inlets.',
    },
    'drain_01.jpg': {
      lat: 19.0720,
      lon: 72.8560,
      addr: 'Tilak Nagar Market Road, Kurla',
      ward: 'Ward 6 - Kurla',
      desc: 'Drainage grate blocked by plastic waste and trash.',
    }
  };

  useEffect(() => {
    api.getSeedImages().then(res => {
      // Filter out resolution/success images for initial submission list
      const initialSeedImages = (res.images || []).filter((img: string) => !img.startsWith('resolved'));
      setImages(initialSeedImages);
    }).catch(console.error);
  }, []);

  // Debounced Nominatim Geocoding Search (>= 500ms debounce)
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      setSearchError(null);
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    const timer = setTimeout(async () => {
      try {
        const res = await api.geocode(searchQuery.trim());
        const items = res.results || [];
        setSearchResults(items);
        setShowDropdown(true);
        if (items.length === 0) {
          setSearchError('No matching address found. Try a broader location or click the map directly.');
        }
      } catch (err: any) {
        console.warn('Geocoding service error:', err);
        setSearchError('Address search service is unreachable. You can use GPS or tap the map directly.');
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 550);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside to dismiss search suggestions
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleSelectAddress = (item: GeocodeResult) => {
    const lat = item.latitude.toFixed(6);
    const lon = item.longitude.toFixed(6);
    setLatitude(lat);
    setLongitude(lon);
    setLocationName(item.display_name);
    setSearchQuery(item.display_name.split(',')[0]);
    setShowDropdown(false);
    setLocationStatus('success');
  };

  // Synchronize Leaflet map with coordinate states & interactive pin placement
  useEffect(() => {
    const container = document.getElementById('report-map');
    if (!container) return;

    const latVal = parseFloat(latitude);
    const lonVal = parseFloat(longitude);
    const hasValidCoords = !isNaN(latVal) && !isNaN(lonVal);

    // Default to Mumbai center if no coordinates selected yet
    const centerLat = hasValidCoords ? latVal : 19.0760;
    const centerLon = hasValidCoords ? lonVal : 72.8777;
    const zoomLevel = hasValidCoords ? 15 : 12;

    const customIcon = L.divIcon({
      html: `<div style="
        background-color: var(--accent-blue, #2563eb); 
        width: 16px; 
        height: 16px; 
        border-radius: 50%; 
        border: 2px solid white; 
        box-shadow: 0 0 8px rgba(37,99,235,0.6);
        cursor: grab;
      "></div>`,
      className: 'custom-gps-marker',
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });

    if (!mapRef.current) {
      const map = L.map('report-map', {
        zoomControl: true,
      }).setView([centerLat, centerLon], zoomLevel);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      // Interactive Click-to-Pin on map
      map.on('click', (e: L.LeafletMouseEvent) => {
        const clickLat = e.latlng.lat.toFixed(6);
        const clickLon = e.latlng.lng.toFixed(6);
        setLatitude(clickLat);
        setLongitude(clickLon);
        setLocationStatus('success');
        setLocationName(`Pinned Location (${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)})`);
      });

      mapRef.current = map;
    } else {
      mapRef.current.setView([centerLat, centerLon], zoomLevel);
      setTimeout(() => {
        if (mapRef.current) mapRef.current.invalidateSize();
      }, 100);
    }

    if (hasValidCoords) {
      if (markerRef.current) {
        markerRef.current.setLatLng([latVal, lonVal]);
      } else {
        const marker = L.marker([latVal, lonVal], { icon: customIcon, draggable: true }).addTo(mapRef.current);
        marker.on('dragend', (e: any) => {
          const pos = e.target.getLatLng();
          setLatitude(pos.lat.toFixed(6));
          setLongitude(pos.lng.toFixed(6));
          setLocationStatus('success');
        });
        markerRef.current = marker;
      }
    } else {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
    }
  }, [latitude, longitude, inputMode]);

  // Cleanup map on component unmount
  useEffect(() => {
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        markerRef.current = null;
      }
    };
  }, []);

  // Demo selection handler
  const handleSelectDemoImage = (img: string) => {
    setSelectedDemoImage(img);
    const preset = PRESET_COORDS[img];
    if (preset) {
      setDescription(preset.desc);
      setLocationName(preset.addr);
      setLatitude(String(preset.lat));
      setLongitude(String(preset.lon));
    }
  };

  // Browser Geolocation
  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }
    setLocationStatus('detecting');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(String(position.coords.latitude.toFixed(6)));
        setLongitude(String(position.coords.longitude.toFixed(6)));
        setLocationName('Current Location');
        setLocationStatus('success');
      },
      (error) => {
        console.error(error);
        setLocationStatus('denied');
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  // Drag and Drop validation helpers
  const handleFile = (file: File) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Unsupported file format. Only JPG, PNG, and WEBP are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds the 10 MB limit.');
      return;
    }
    setUploadedFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setFilePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  // Drag Handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setFilePreview('');
  };

  // Form Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validations
    if (inputMode === 'UPLOAD' && !uploadedFile) {
      alert('Please upload a civic issue photo.');
      return;
    }
    if (inputMode === 'DEMO' && !selectedDemoImage) {
      alert('Please select a demo image.');
      return;
    }
    if (!latitude || !longitude) {
      alert('Location is required. Please use "Use My Current Location" to capture your GPS coordinates.');
      return;
    }

    setSubmitting(true);
    try {
      // Automatically map ward based on coordinate presets, fallback to general ward
      let calculatedWard = 'Ward 1 - Municipal General';
      if (inputMode === 'DEMO' && selectedDemoImage) {
        calculatedWard = PRESET_COORDS[selectedDemoImage]?.ward || calculatedWard;
      }

      const payload = {
        citizen_name: citizenName,
        phone,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        address: locationName || 'Unknown Location',
        ward: calculatedWard,
        description,
        image_filename: inputMode === 'DEMO' ? selectedDemoImage : undefined,
        image_file: inputMode === 'UPLOAD' ? uploadedFile : null,
      };

      const res = await api.submitReport(payload);
      setSubmittedReport(res);
    } catch (err: any) {
      console.error(err);
      alert(`Submission failed: ${err.message || err}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)' }}>
          Submit Citizen Report
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Submit a new civic grievance complaint. Choose between real image uploads with automatic GPS detection, or pre-seeded scenario images to trigger demo clustering.
        </p>
      </div>

      {!submittedReport ? (
        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
          
          {/* Segmented Selector for Input Mode */}
          <div style={{
            display: 'flex',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-primary)',
            borderRadius: 8,
            padding: 4,
            width: 'fit-content',
            marginBottom: 4,
          }}>
            <button
              type="button"
              className={`btn ${inputMode === 'UPLOAD' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => {
                setInputMode('UPLOAD');
                removeFile();
                setSelectedDemoImage('');
                setLatitude('');
                setLongitude('');
                setLocationName('');
                setLocationStatus('idle');
              }}
              style={{ border: 'none', padding: '6px 16px', fontSize: 12 }}
            >
              Upload Your Photo
            </button>
            <button
              type="button"
              className={`btn ${inputMode === 'DEMO' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => {
                setInputMode('DEMO');
                removeFile();
                setSelectedDemoImage('');
                setLatitude('');
                setLongitude('');
                setLocationName('');
                setLocationStatus('idle');
              }}
              style={{ border: 'none', padding: '6px 16px', fontSize: 12 }}
            >
              Choose Demo Image
            </button>
          </div>

          {/* UPLOAD MODE VIEW */}
          {inputMode === 'UPLOAD' && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                Report Issue Photo
              </label>

              {!filePreview ? (
                /* Drag & Drop Input Area */
                <div
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  style={{
                    border: `2px dashed ${dragActive ? 'var(--accent-blue)' : 'var(--border-secondary)'}`,
                    borderRadius: 8,
                    background: dragActive ? 'rgba(37, 99, 235, 0.04)' : 'var(--bg-primary)',
                    padding: '32px 16px',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 12,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                  onClick={() => document.getElementById('citizen-photo-input')?.click()}
                >
                  <UploadCloud size={32} color={dragActive ? 'var(--accent-blue)' : 'var(--text-tertiary)'} />
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
                      Upload Civic Issue Photo
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                      Drag and drop an image here or click to browse
                    </div>
                  </div>
                  
                  <input
                    id="citizen-photo-input"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                  />

                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ fontSize: 11, padding: '4px 12px' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      document.getElementById('citizen-photo-input')?.click();
                    }}
                  >
                    CHOOSE IMAGE
                  </button>

                  <div style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
                    JPG, PNG, WEBP • Max 10 MB
                  </div>
                </div>
              ) : (
                /* Preview Area */
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  padding: 12,
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 8,
                }}>
                  <img
                    src={filePreview}
                    alt="Citizen Upload Preview"
                    style={{
                      width: 90,
                      height: 70,
                      borderRadius: 6,
                      objectFit: 'cover',
                      border: '1px solid var(--border-primary)'
                    }}
                  />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>Image Selected</span>
                      <span style={{ fontSize: 10, color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                        File: {uploadedFile?.name}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => document.getElementById('citizen-photo-input')?.click()}
                        style={{ fontSize: 10, padding: '3px 8px' }}
                      >
                        Replace Image
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger"
                        onClick={removeFile}
                        style={{ fontSize: 10, padding: '3px 8px' }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* DEMO MODE VIEW */}
          {inputMode === 'DEMO' && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                  Choose Demo Scenario Image
                </label>
                <span className="badge badge-medium" style={{ fontSize: 9 }}>DEMO MODE</span>
              </div>
              <div className="seed-image-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 10 }}>
                {images.map((img) => (
                  <div
                    key={img}
                    className={`seed-image-card ${selectedDemoImage === img ? 'selected' : ''}`}
                    onClick={() => handleSelectDemoImage(img)}
                    style={{
                      borderWidth: 2,
                      borderStyle: 'solid',
                      borderColor: selectedDemoImage === img ? 'var(--accent-blue)' : 'transparent',
                      borderRadius: 8,
                      overflow: 'hidden',
                      background: 'var(--bg-primary)',
                    }}
                  >
                    <img
                      src={`${API_BASE}/seed-images/${img}`}
                      alt={img}
                      style={{ width: '100%', height: 90, objectFit: 'cover' }}
                    />
                    <div style={{ padding: 6, fontSize: 10, textAlign: 'center', color: 'var(--text-secondary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                      {img}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contact Details Card */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Contact Details</h3>
              <div>
                <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>Name</label>
                <input
                  className="input"
                  value={citizenName}
                  onChange={(e) => setCitizenName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>Phone</label>
                <input
                  className="input"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Location Manager Details Card */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Report Location</h3>

              {inputMode === 'UPLOAD' ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {/* Address Search Bar (OpenStreetMap Nominatim via Backend Proxy) */}
                  <div ref={searchContainerRef} style={{ position: 'relative', width: '100%' }}>
                    <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>
                      Search Address or Landmark (OpenStreetMap Nominatim)
                    </label>
                    <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                      <Search size={14} color="var(--text-tertiary)" style={{ position: 'absolute', left: 10, pointerEvents: 'none' }} />
                      <input
                        type="text"
                        className="input"
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          setShowDropdown(true);
                        }}
                        onFocus={() => {
                          if (searchResults.length > 0) setShowDropdown(true);
                        }}
                        placeholder="Search street, area or landmark (e.g. Chakala, Bandra West, Dadar)..."
                        style={{ paddingLeft: 32, paddingRight: 32, fontSize: 12 }}
                      />
                      {isSearching && (
                        <Loader2 size={14} color="var(--accent-blue)" className="animate-spin" style={{ position: 'absolute', right: 10 }} />
                      )}
                      {!isSearching && searchQuery && (
                        <button
                          type="button"
                          onClick={() => {
                            setSearchQuery('');
                            setSearchResults([]);
                            setShowDropdown(false);
                            setSearchError(null);
                          }}
                          style={{
                            position: 'absolute',
                            right: 8,
                            background: 'none',
                            border: 'none',
                            color: 'var(--text-tertiary)',
                            cursor: 'pointer',
                            padding: 2,
                            display: 'flex',
                            alignItems: 'center'
                          }}
                        >
                          <X size={14} />
                        </button>
                      )}
                    </div>

                    {/* Geocoding Suggestions Dropdown */}
                    {showDropdown && searchResults.length > 0 && (
                      <div style={{
                        position: 'absolute',
                        top: '100%',
                        left: 0,
                        right: 0,
                        zIndex: 1000,
                        marginTop: 4,
                        background: 'var(--bg-secondary)',
                        border: '1px solid var(--border-primary)',
                        borderRadius: 8,
                        boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
                        maxHeight: 220,
                        overflowY: 'auto',
                      }}>
                        {searchResults.map((item, idx) => (
                          <div
                            key={idx}
                            onClick={() => handleSelectAddress(item)}
                            style={{
                              padding: '8px 12px',
                              cursor: 'pointer',
                              borderBottom: idx < searchResults.length - 1 ? '1px solid var(--border-secondary)' : 'none',
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: 8,
                              transition: 'background 0.15s ease',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                          >
                            <MapPin size={14} color="var(--accent-blue)" style={{ marginTop: 2, flexShrink: 0 }} />
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 2, overflow: 'hidden' }}>
                              <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                                {item.display_name.split(',')[0]}
                              </span>
                              <span style={{ fontSize: 10, color: 'var(--text-secondary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                                {item.display_name}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Friendly Unreachable / Notice Message */}
                    {searchError && (
                      <div style={{
                        marginTop: 6,
                        padding: '6px 10px',
                        borderRadius: 6,
                        background: 'rgba(245, 158, 11, 0.1)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                        fontSize: 11,
                        color: '#fbbf24',
                      }}>
                        <AlertTriangle size={13} style={{ flexShrink: 0 }} />
                        <span>{searchError}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions: GPS Auto-Detect & Map Pin Instructions */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={handleGetLocation}
                      style={{ fontSize: 11, padding: '6px 14px', gap: 6 }}
                    >
                      <Compass size={14} />
                      {locationStatus === 'detecting' ? 'Detecting GPS…' : 'Use My Current Location'}
                    </button>
                    <span style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
                      📍 Or tap/drag the map pin below
                    </span>
                  </div>

                  {/* Selected Coordinates Status Pill */}
                  {latitude && longitude && (
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '8px 12px',
                      background: 'rgba(34, 197, 94, 0.08)',
                      border: '1px solid rgba(34, 197, 94, 0.25)',
                      borderRadius: 6,
                      fontSize: 11,
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <CheckCircle2 size={14} color="#22c55e" style={{ flexShrink: 0 }} />
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Selected Pin:</span>
                        <span className="font-mono" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>
                          {latitude}, {longitude}
                        </span>
                      </div>
                      <span style={{ fontSize: 10, color: 'var(--text-secondary)', maxWidth: 180, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                        {locationName || 'Custom Coordinate'}
                      </span>
                    </div>
                  )}

                  {locationStatus === 'denied' && (
                    <div style={{
                      padding: '8px 10px',
                      borderRadius: 6,
                      background: 'rgba(239, 68, 68, 0.08)',
                      border: '1px solid rgba(239, 68, 68, 0.25)',
                      fontSize: 11,
                      color: '#ef4444',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6
                    }}>
                      <AlertTriangle size={13} />
                      <span>Location permission denied. Please search an address above or tap the map directly.</span>
                    </div>
                  )}
                </div>
              ) : (
                /* Static Display fields for Demo Mode */
                selectedDemoImage ? (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '12px 14px',
                    borderRadius: 8,
                    background: 'rgba(37, 99, 235, 0.06)',
                    border: '1px solid rgba(37, 99, 235, 0.15)',
                  }}>
                    <MapPin size={18} color="var(--accent-blue)" />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>📍 Demo Location</span>
                      <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                        {PRESET_COORDS[selectedDemoImage]?.addr} — {PRESET_COORDS[selectedDemoImage]?.ward}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: '100%', color: 'var(--text-tertiary)', fontSize: 12 }}>
                    <Landmark size={18} />
                    Choose a seed image above to set geo-coordinates
                  </div>
                )
              )}

              {/* Leaflet Interactive Map */}
              {(inputMode === 'UPLOAD' || (latitude && longitude)) && (
                <div 
                  id="report-map" 
                  style={{ 
                    height: '210px', 
                    width: '100%', 
                    borderRadius: '8px', 
                    marginTop: '6px',
                    border: '1px solid var(--border-primary)',
                    zIndex: 10,
                    cursor: 'crosshair',
                  }}
                />
              )}
            </div>
          </div>

          {/* Description Card */}
          <div className="card">
            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
              Description
            </label>
            <textarea
              className="input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide a brief description of the issue..."
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || (inputMode === 'UPLOAD' && !uploadedFile) || (inputMode === 'DEMO' && !selectedDemoImage)}
            style={{ padding: 12, justifyContent: 'center' }}
          >
            {submitting ? (
              <span className="spinner" />
            ) : (
              <>
                <FilePlus size={16} />
                Submit Complaint Report
              </>
            )}
          </button>
        </form>
      ) : (
        /* Submission Success View */
        <div className="card" style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          textAlign: 'center',
          gap: 16,
        }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            background: 'var(--status-resolved-bg)',
            border: '1px solid var(--status-resolved)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <ClipboardCheck size={24} color="var(--status-resolved)" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
              Grievance Successfully Filed
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Your complaint has been logged under ID: <strong className="font-mono" style={{ color: 'var(--accent-blue)' }}>{submittedReport.report_id}</strong>
            </p>
          </div>

          <div style={{
            display: 'flex',
            gap: 12,
            marginTop: 12,
          }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setSubmittedReport(null);
                setUploadedFile(null);
                setFilePreview('');
                setSelectedDemoImage('');
                setLatitude('');
                setLongitude('');
                setLocationName('');
                setDescription('');
              }}
            >
              Submit Another Report
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                navigate('/dashboard', { state: { autoAnalyzeId: submittedReport.report_id } });
              }}
            >
              Go to Dashboard and Analyze
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
