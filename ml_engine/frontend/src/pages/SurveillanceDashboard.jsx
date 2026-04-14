import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { toggleNightVisionCam, startLiveStream } from '../api/apiClient';

const SurveillanceDashboard = () => {
  const [nightVision, setNightVision] = useState(false);
  const [activeTarget, setActiveTarget] = useState(null);
  const [detections, setDetections] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({ fps: 0, threat_counts: {}, zone_counts: {} });
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to Backend WebSocket
    const connectWS = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log("Connected to AI Backend");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'detections') {
          setDetections(data.detections || []);
          setStats({
            fps: data.fps,
            threat_counts: data.threat_counts || {},
            zone_counts: data.zone_counts || {}
          });
          
          // Update persistent alert list
          if (data.alerts && data.alerts.length > 0) {
            setAlerts(prev => {
              const newAlerts = [...data.alerts, ...prev];
              return newAlerts.slice(0, 20); // Keep last 20
            });
          }
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("Disconnected from AI Backend. Retrying...");
        setTimeout(connectWS, 3000);
      };

      wsRef.current = ws;
    };

    connectWS();
    return () => wsRef.current?.close();
  }, []);

  const handleLiveStream = async () => {
    toast.loading('Connecting to live stream...', { id: 'stream' });
    await startLiveStream();
    toast.success('Live stream connected securely.', { id: 'stream' });
  };

  const handleNightVisionToggle = async () => {
    const newState = !nightVision;
    toast.loading('Adjusting optical array...', { id: 'nv' });
    await toggleNightVisionCam(newState);
    setNightVision(newState);
    toast.success(`NIGHT_VISION: ${newState ? 'ON' : 'OFF'}`, { id: 'nv', icon: '🌙' });
  };

  return (
    <>
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Live Alert Feed */}
        <section className="w-80 bg-surface-container-low border-r border-outline-variant/10 overflow-y-auto p-4 flex flex-col gap-4">
          <div className="flex justify-between items-center border-b border-outline-variant/20 pb-2">
            <span className="font-headline text-[10px] tracking-[0.2em] font-black uppercase text-on-surface">Live Alert Feed</span>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-inverse-primary animate-pulse' : 'bg-red-500'}`}></span>
          </div>
          {/* Dynamic Alert Cards */}
          <div className="space-y-2">
            {alerts.length === 0 ? (
              <div className="text-[10px] font-mono text-zinc-500 text-center py-10 italic">Waiting for telemetry data...</div>
            ) : (
              alerts.map((alert, idx) => (
                <div 
                  key={`${alert.track_id}-${idx}`}
                  onClick={() => setActiveTarget(alert.track_id)} 
                  className={`bg-surface-container p-3 border-l-2 transition-colors cursor-pointer 
                    ${alert.threat_level === 'HIGH' ? 'border-inverse-primary' : 'border-secondary-container'}
                    ${activeTarget === alert.track_id ? 'bg-surface-container-high ring-1 ring-inverse-primary/50' : 'hover:bg-surface-container-high'}`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-inverse-primary font-headline text-[10px] font-bold">{alert.class_name}#{alert.track_id}</span>
                    <span className={`${alert.threat_level === 'HIGH' ? 'bg-inverse-primary text-white' : 'bg-secondary-container text-on-secondary'} text-[8px] px-1 font-headline font-bold`}>
                      {alert.threat_level}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-y-1 text-[9px] font-mono uppercase text-zinc-400">
                    <span>Zone: {alert.zone_name}</span><span className="text-right">Dist: {alert.distance}M</span>
                    <span className="col-span-2 text-[8px] mt-1 text-zinc-500 truncate">{alert.behaviors?.join(', ')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Central: Video Stream Viewport */}
        <section className="flex-1 bg-black relative flex flex-col">
          {/* HUD Overlays */}
          <div className="absolute inset-0 z-10 pointer-events-none hud-overlay p-6 flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <div className="border-l-2 border-t-2 border-white/40 w-16 h-16"></div>
              <div className="flex flex-col items-center">
                <div className="bg-black/60 px-4 py-1 text-[10px] font-mono tracking-widest text-primary border border-primary/30">
                  CAM_04 // SECTOR_NORTH // 32.789° N, -106.845° W
                </div>
                <div className="mt-2 flex gap-4">
                  <div className="flex items-center gap-1 bg-black/40 px-2 text-[9px] font-mono border border-white/10">
                    <span className="w-1 h-1 bg-tertiary-container rounded-full animate-pulse"></span> REC
                  </div>
                  <div className="bg-black/40 px-2 text-[9px] font-mono border border-white/10">
                    {stats.fps} FPS // 4K // {nightVision ? 'IR_ON' : 'HDR'}
                  </div>
                </div>
              </div>
              <div className="border-r-2 border-t-2 border-white/40 w-16 h-16"></div>
            </div>

            {/* Tactical HUD Content - REMOVED HARDCODED BOXES */}
            <div className="relative w-full h-full">
            </div>

            <div className="flex justify-between items-end">
              <div className="border-l-2 border-b-2 border-white/40 w-16 h-16"></div>
              <div className="w-1/2 h-8 border-x border-t border-white/20 relative">
                <div className="absolute inset-0 flex items-center justify-around text-[8px] font-mono text-zinc-500">
                  <span>2M</span><span>4M</span><span>6M</span><span>8M</span><span>10M</span>
                </div>
                <div className="absolute bottom-0 left-[40%] w-2 h-4 bg-inverse-primary opacity-50 blur-[2px]"></div>
              </div>
              <div className="border-r-2 border-b-2 border-white/40 w-16 h-16"></div>
            </div>
          </div>

          {/* Video Stream Image */}
          <div className="w-full h-full relative overflow-hidden bg-zinc-900 transition-all duration-1000">
            <img 
              className={`w-full h-full object-cover transition-all duration-1000 ${
                nightVision ? 'hue-rotate-90 brightness-75 contrast-150 sepia-[.3]' : ''
              }`} 
              src="http://localhost:8000/video_feed" 
              alt="Surveillance stream" 
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://lh3.googleusercontent.com/aida-public/AB6AXuAT0k-ZdnQ209UiNi30Qb_0I9PjW9dxf7wDnMlSibW2qssHPTYPyLc6jy7XXe0COXNP5VjdJ0vdh-EPI89_sBJNYWcK4g_LmjmAXC_UcWVckRuFPK0feh1cYSzzsfTqq5rD_9X9z-dzyKxLTwHPY8AH-RafmnYa_6b3x0I5xp9d5UO8Nr60826iC5YlGxUFbl9tXUMtRwRXB53gzvDTvxQ5eJrHvT7z4P1aJpSRjQUUAAHitFl9Tv28WTtRsB-alGTcmlEzU5Vpxko"
              }}
            />
            <div className="absolute inset-0 scanline opacity-30 pointer-events-none"></div>
          </div>

          {/* Control Bar */}
          <div className="bg-surface-container-low h-12 border-t border-outline-variant/10 flex items-center px-4 gap-6">
            <div className="flex gap-2">
              <button onClick={handleLiveStream} className="bg-inverse-primary text-white text-[10px] font-headline font-bold px-4 py-1 flex items-center gap-2 hover:opacity-80 active:scale-95 transition-all">
                <span className="material-symbols-outlined text-[14px]">videocam</span> LIVE_STREAM
              </button>
              <button 
                onClick={handleNightVisionToggle} 
                className={`text-[10px] font-headline font-bold px-4 py-1 flex items-center gap-2 hover:bg-white/10 active:scale-95 transition-all ${
                  nightVision ? 'bg-tertiary-container text-white' : 'bg-surface-container-highest text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[14px]">nightlight</span> NIGHT_VISION: {nightVision ? 'ON' : 'OFF'}
              </button>
            </div>
            <div className="flex-1"></div>
            <div className="flex items-center gap-4 text-zinc-500 font-mono text-[10px]">
              <span className="flex items-center gap-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-tertiary-container' : 'bg-red-500'}`}></span> 
                {isConnected ? 'AI_READY' : 'BACKEND_OFFLINE'}
              </span>
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-tertiary-container rounded-full"></span> OPTICS_CALIBRATED</span>
            </div>
          </div>
        </section>

        {/* Right Panel: Radar Map */}
        <section className="w-80 bg-surface-container border-l border-outline-variant/10 flex flex-col hidden lg:flex">
          <div className="p-4 border-b border-outline-variant/20">
            <span className="font-headline text-[10px] tracking-[0.2em] font-black uppercase text-on-surface">Tactical Radar</span>
          </div>
          <div className="flex-1 relative bg-[#0e0e10] p-4 flex items-center justify-center">
            <div className="absolute inset-0 opacity-20" style={{backgroundImage: 'radial-gradient(circle, #603e39 1px, transparent 1px)', backgroundSize: '20px 20px'}}></div>
            <div className="relative w-full aspect-square border border-outline-variant/30 rounded-full flex items-center justify-center overflow-hidden">
              <div className="w-3/4 h-3/4 border border-outline-variant/20 rounded-full"></div>
              <div className="w-1/2 h-1/2 border border-outline-variant/20 rounded-full"></div>
              <div className="w-1/4 h-1/4 border border-outline-variant/20 rounded-full"></div>
              <div className="absolute w-full h-[1px] bg-outline-variant/30"></div>
              <div className="absolute h-full w-[1px] bg-outline-variant/30"></div>
              
              {/* Dynamic Radar Targets */}
              {detections.map(det => {
                const [wx, wy] = det.world_pos || [0, 0];
                const maxDistY = 40.0; // Max depth 40m
                const maxDistX = 20.0; // Max width +/- 10m visible
                
                // Scale meters to %
                // X: center is 50%, +/- 10m
                const left = 50 + (wx / maxDistX) * 50;
                // Y: camera is at bottom (100%), 40m ahead is top (0%)
                const top = 100 - (wy / maxDistY) * 100;
                
                // Clamp within circle
                const clampedTop = Math.max(0, Math.min(100, top));
                const clampedLeft = Math.max(0, Math.min(100, left));
                
                return (
                  <div 
                    key={det.track_id}
                    style={{ left: `${clampedLeft}%`, top: `${clampedTop}%` }}
                    className={`absolute w-2 h-2 rounded-none transition-all duration-300 transform -translate-x-1/2 -translate-y-1/2
                      ${det.threat_level === 'HIGH' ? 'bg-inverse-primary shadow-[0_0_10px_rgba(192,1,0,0.8)] animate-pulse' : 
                        det.threat_level === 'SUSPICIOUS' ? 'bg-secondary-container shadow-[0_0_8px_rgba(255,191,0,0.6)]' : 'bg-tertiary'}`}
                  >
                    <span className="absolute -top-3 left-3 text-[6px] font-mono text-white whitespace-nowrap">ID:{det.track_id}</span>
                  </div>
                );
              })}

              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-yellow-400 rounded-full shadow-[0_0_10px_rgba(255,255,0,0.8)]"></div>
              <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-transparent via-transparent to-primary/5 border-r border-primary/20 rotate-45"></div>
            </div>
          </div>
          <div className="p-4 bg-surface-container-low border-t border-outline-variant/10">
            <div className="text-[9px] font-mono text-zinc-500 mb-2 uppercase">Target Metrics:</div>
            <div className="space-y-1">
              <div className="flex justify-between text-[10px] font-headline uppercase"><span className="text-zinc-400">Total Tracked</span><span className="text-on-surface">{detections.length} ACTIVE</span></div>
              <div className="flex justify-between text-[10px] font-headline uppercase"><span className="text-zinc-400">High Threat</span><span className="text-on-surface text-inverse-primary">{stats.threat_counts?.HIGH || 0}</span></div>
              <div className="flex justify-between text-[10px] font-headline uppercase"><span className="text-zinc-400">Suspicious</span><span className="text-on-surface text-secondary-container">{stats.threat_counts?.SUSPICIOUS || 0}</span></div>
            </div>
          </div>
        </section>
      </div>

      {/* Bottom Analytics Widgets */}
      <footer className="h-32 bg-[#0e0e10] border-t-[0.5px] border-[#603e39]/15 flex items-stretch">
        <div className="w-1/4 border-r border-outline-variant/10 p-3 flex flex-col justify-between">
          <span className="text-[9px] font-mono text-zinc-500 uppercase">Detection Analytics</span>
          <div className="flex items-end gap-2 h-12">
            <div className="flex-1 bg-surface-container h-[40%]"></div>
            <div className="flex-1 bg-surface-container h-[60%]"></div>
            <div className="flex-1 bg-surface-container-high h-[90%] border-t border-inverse-primary"></div>
            <div className="flex-1 bg-surface-container h-[55%]"></div>
            <div className="flex-1 bg-surface-container h-[30%]"></div>
            <div className="flex-1 bg-surface-container h-[75%]"></div>
          </div>
          <div className="flex justify-between items-center mt-1">
            <span className="text-[10px] font-headline font-bold">Threat Volume (Live)</span>
            <span className="text-[10px] text-inverse-primary">{stats.fps} FPS</span>
          </div>
        </div>
        <div className="w-2/4 border-r border-outline-variant/10 p-3 grid grid-cols-3 gap-4">
          <div className="bg-surface-container-low border-l-2 border-inverse-primary p-2 flex flex-col justify-center">
            <span className="text-[8px] font-mono text-zinc-500 uppercase">High Threat</span>
            <span className="text-2xl font-black font-headline text-inverse-primary">{stats.threat_counts?.HIGH || 0}</span>
          </div>
          <div className="bg-surface-container-low border-l-2 border-secondary-container p-2 flex flex-col justify-center">
            <span className="text-[8px] font-mono text-zinc-500 uppercase">Suspicious</span>
            <span className="text-2xl font-black font-headline text-secondary-container">{stats.threat_counts?.SUSPICIOUS || 0}</span>
          </div>
          <div className="bg-surface-container-low border-l-2 border-tertiary p-2 flex flex-col justify-center">
            <span className="text-[8px] font-mono text-zinc-500 uppercase">Normal</span>
            <span className="text-2xl font-black font-headline text-tertiary">{stats.threat_counts?.NORMAL || 0}</span>
          </div>
        </div>
        <div className="w-1/4 p-3 flex flex-col justify-between">
          <div className="flex justify-between text-[9px] font-mono text-zinc-500 uppercase">
            <span>Zone Status</span>
            <span>Active</span>
          </div>
          <div className="space-y-1.5 mt-2">
            <div className="flex items-center gap-2"><span className="text-[8px] font-headline w-12">RED</span><div className="flex-1 h-1 bg-surface-container-highest overflow-hidden"><div style={{width: `${(stats.zone_counts?.ZONE_3 || 0) * 20}%`}} className="h-full bg-inverse-primary transition-all duration-500"></div></div></div>
            <div className="flex items-center gap-2"><span className="text-[8px] font-headline w-12">YELLOW</span><div className="flex-1 h-1 bg-surface-container-highest overflow-hidden"><div style={{width: `${(stats.zone_counts?.ZONE_2 || 0) * 20}%`}} className="h-full bg-secondary-container transition-all duration-500"></div></div></div>
            <div className="flex items-center gap-2"><span className="text-[8px] font-headline w-12">GREEN</span><div className="flex-1 h-1 bg-surface-container-highest overflow-hidden"><div style={{width: `${(stats.zone_counts?.ZONE_1 || 0) * 20}%`}} className="h-full bg-tertiary transition-all duration-500"></div></div></div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default SurveillanceDashboard;
