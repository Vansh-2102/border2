import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { deployDroneToTarget, dismissAlert } from '../api/apiClient';

const SpatialAnalytics = () => {
    const [mapStyle, setMapStyle] = useState('TOPOGRAPHIC'); // TOPOGRAPHIC or THERMAL
    const [hiddenLogs, setHiddenLogs] = useState([]);
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await fetch('http://localhost:8000/logs');
                const data = await response.json();
                if (data.success) {
                    setLogs(data.logs);
                }
            } catch (error) {
                console.error("Failed to fetch logs:", error);
            }
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleDeployDrone = async (logId) => {
        toast.loading(`Deploying drone to intercept ${logId}...`, { id: logId });
        await deployDroneToTarget(logId);
        toast.success(`Drone en route to sequence ${logId}.`, { id: logId, icon: '🚁' });
    };

    const handleDismiss = async (logId) => {
        await dismissAlert(logId);
        setHiddenLogs([...hiddenLogs, logId]);
        toast(`Log ${logId} dismissed.`, { icon: '✖️' });
    };

    return (
      <div className="flex-grow p-6 pt-12 pb-24 overflow-y-auto">
        {/* Page Header */}
        <header className="flex justify-between items-end mb-10">
          <div>
            <h1 className="font-headline text-3xl font-black tracking-tighter uppercase text-on-surface">Historical Data_Logs</h1>
            <p className="font-label text-[10px] tracking-[0.2em] text-zinc-500 uppercase mt-1">Real-time processing for sector alpha-9</p>
          </div>
          <div className="flex gap-4">
            <div className="bg-surface-container border-l-2 border-primary-container px-4 py-2">
              <div className="text-[9px] font-mono text-zinc-500 uppercase">Detection Rate</div>
              <div className="text-xl font-headline font-bold text-tertiary">98.4%</div>
            </div>
            <div className="bg-surface-container border-l-2 border-inverse-primary px-4 py-2">
              <div className="text-[9px] font-mono text-zinc-500 uppercase">Critical Threats</div>
              <div className="text-xl font-headline font-bold text-inverse-primary">{logs.filter(l => l.type === 'HIGH').length}</div>
            </div>
          </div>
        </header>

        {/* Bento Grid Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[200px]">
          {/* ... (keep charts as they are for now) ... */}
          <div className="md:col-span-8 md:row-span-2 bg-surface-container p-6 relative overflow-hidden flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-label text-xs font-bold tracking-widest uppercase flex items-center">
                <span className="w-2 h-2 bg-inverse-primary mr-2"></span> Target Frequency_24H
              </h3>
              <div className="flex space-x-2">
                <span className="text-[9px] font-mono text-tertiary px-2 py-0.5 bg-tertiary/10">LIVE_FEED</span>
                <span className="text-[9px] font-mono text-zinc-500">SYNC: 120ms</span>
              </div>
            </div>
            
            <div className="flex-grow relative mt-4 flex items-end justify-between px-2">
              <div className="absolute inset-0 flex flex-col justify-between opacity-10 pointer-events-none">
                <div className="border-t border-zinc-500 w-full"></div>
                <div className="border-t border-zinc-500 w-full"></div>
                <div className="border-t border-zinc-500 w-full"></div>
                <div className="border-t border-zinc-500 w-full"></div>
              </div>
              <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                <path d="M0,80 Q10,70 20,85 T40,60 T60,75 T80,40 T100,50" fill="none" stroke="#c00100" strokeWidth="2"></path>
                <path d="M0,80 Q10,70 20,85 T40,60 T60,75 T80,40 T100,50 V100 H0 Z" fill="url(#line-grad)" opacity="0.2"></path>
                <defs>
                  <linearGradient id="line-grad" x1="0%" x2="0%" y1="0%" y2="100%">
                    <stop offset="0%" style={{stopColor: "#c00100", stopOpacity: 1}}></stop>
                    <stop offset="100%" style={{stopColor: "#c00100", stopOpacity: 0}}></stop>
                  </linearGradient>
                </defs>
              </svg>
              <div className="w-full absolute bottom-0 flex justify-between text-[8px] font-mono text-zinc-600 uppercase pt-2">
                <span>00:00</span><span>04:00</span><span>08:00</span><span>12:00</span><span>16:00</span><span>20:00</span><span>23:59</span>
              </div>
            </div>
          </div>
          
          {/* Doughnut Chart */}
          <div className="md:col-span-4 md:row-span-2 bg-surface-container p-6 flex flex-col">
            <h3 className="font-label text-xs font-bold tracking-widest uppercase mb-8 flex items-center">
              <span className="w-2 h-2 bg-secondary mr-2"></span> Threat Distribution
            </h3>
            <div className="flex-grow flex items-center justify-center relative">
              <div className="w-40 h-40 rounded-full border-[12px] border-zinc-800 relative flex items-center justify-center">
                <div className="absolute inset-[-12px] rounded-full border-[12px] border-t-inverse-primary border-r-secondary border-b-tertiary border-l-transparent rotate-45"></div>
                <div className="text-center">
                  <div className="text-2xl font-black font-headline tracking-tighter">{logs.length}</div>
                  <div className="text-[8px] font-mono text-zinc-500 uppercase tracking-tighter">Total Events</div>
                </div>
              </div>
            </div>
            <div className="space-y-3 mt-6">
              <div className="flex justify-between items-center"><div className="flex items-center text-[10px] font-mono text-zinc-400"><div className="w-2 h-2 bg-inverse-primary mr-2"></div> LEVEL_A (CRITICAL)</div><span className="text-[10px] font-bold text-on-surface">{Math.round((logs.filter(l => l.type === 'HIGH').length / (logs.length || 1)) * 100)}%</span></div>
              <div className="flex justify-between items-center"><div className="flex items-center text-[10px] font-mono text-zinc-400"><div className="w-2 h-2 bg-secondary mr-2"></div> LEVEL_B (WARNING)</div><span className="text-[10px] font-bold text-on-surface">{Math.round((logs.filter(l => l.type === 'SUSPICIOUS').length / (logs.length || 1)) * 100)}%</span></div>
              <div className="flex justify-between items-center"><div className="flex items-center text-[10px] font-mono text-zinc-400"><div className="w-2 h-2 bg-tertiary mr-2"></div> LEVEL_C (ROUTINE)</div><span className="text-[10px] font-bold text-on-surface">{Math.round((logs.filter(l => l.type === 'NORMAL').length / (logs.length || 1)) * 100)}%</span></div>
            </div>
          </div>
          
          {/* Heatmap */}
          <div className="md:col-span-8 md:row-span-2 bg-surface-container-low overflow-hidden relative group">
            <div className="absolute top-4 left-6 z-10 p-1 bg-surface-container/80 backdrop-blur-md">
              <h3 className="font-label text-xs font-bold tracking-widest uppercase flex items-center text-on-surface">
                <span className="w-2 h-2 bg-tertiary mr-2"></span> Heatmap: Sector_Delta
              </h3>
            </div>
            <div className="absolute bottom-4 left-6 z-10 flex space-x-2">
              <button onClick={() => setMapStyle('TOPOGRAPHIC')} className={`px-3 py-1 text-[9px] font-mono transition-colors ${mapStyle === 'TOPOGRAPHIC' ? 'bg-surface-container-highest text-white border-l-2 border-primary' : 'bg-surface-container text-zinc-500 hover:text-white'}`}>TOPOGRAPHIC</button>
              <button onClick={() => setMapStyle('THERMAL')} className={`px-3 py-1 text-[9px] font-mono transition-colors ${mapStyle === 'THERMAL' ? 'bg-surface-container-highest text-white border-l-2 border-primary' : 'bg-surface-container text-zinc-500 hover:text-white'}`}>THERMAL</button>
            </div>
            
            <div className={`w-full h-full transition-all duration-1000 ${
                mapStyle === 'THERMAL' ? 'grayscale opacity-70 sepia-[.4] hue-rotate-180 mix-blend-screen' : 'grayscale opacity-50 contrast-125'
            }`}>
              <img alt="Satellite Border Map" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB-Ai1whrxQHtWYTHdpufQo6RPK0Vi7XKFJmQy2es7Wbaqn86VRKjLRL-2NJ4SX3H5W_MwvrIVawvXnVBWTuenTbdpb30PLOtql_JPAogQm9R9m5T0tnLLOjU0D_I-VF16Qi9XHfpIm5vqK4yeYWDLKpzgDFwd2Hhoowponuz7pVAun77PXgAbhlb0L-1obATs_Elp36xIlgyc9Pspn6GHiY_Lbe1h0dgeQoZz7bc4AxZRySr9rEPuummBHt0eLfPRu8rIhRc9DZc8"/>
            </div>
            <div className="absolute inset-0 scanline pointer-events-none opacity-20"></div>
          </div>
          
          {/* List: Tactical Logs */}
          <div className="md:col-span-4 md:row-span-2 bg-surface-container-low flex flex-col">
            <div className="p-6 border-b border-outline-variant/10">
              <h3 className="font-label text-xs font-bold tracking-widest uppercase flex items-center">
                <span className="material-symbols-outlined text-[14px] mr-2">history</span> Recent_Intercepts
              </h3>
            </div>
            <div className="flex-grow overflow-y-auto mask-fade-bottom">
              <div className="divide-y divide-outline-variant/5">
                {logs.length === 0 ? (
                  <div className="p-10 text-center text-[10px] font-mono text-zinc-500 uppercase">No historical data logs found in buffer.</div>
                ) : (
                  logs.filter(log => !hiddenLogs.includes(log.id)).map(log => (
                    <div key={log.id} className="px-6 py-4 hover:bg-white/5 transition-colors group relative">
                      <div className="flex justify-between mb-1">
                        <span className={`text-[9px] font-mono font-bold ${log.type === 'HIGH' ? 'text-inverse-primary' : log.type === 'SUSPICIOUS' ? 'text-secondary' : 'text-tertiary'}`}>
                          {log.type === 'HIGH' ? 'CRITICAL_EVENT' : log.type === 'SUSPICIOUS' ? 'WARNING' : 'ROUTINE'}
                        </span>
                        <span className="text-[9px] font-mono text-zinc-500">{log.timestamp}</span>
                      </div>
                      <div className="text-[11px] text-zinc-300 font-mono leading-tight">{log.message}</div>
                      <div className="mt-3 flex items-center space-x-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => handleDeployDrone(log.id)} className="flex items-center gap-1 text-[8px] font-bold text-[#4edea3] cursor-pointer hover:underline uppercase">
                          <span className="material-symbols-outlined text-[10px]">flight_takeoff</span> DEPLOY_DRONE
                        </button>
                        <button onClick={() => handleDismiss(log.id)} className="flex items-center gap-1 text-[8px] font-bold text-zinc-500 cursor-pointer hover:text-white uppercase">
                          <span className="material-symbols-outlined text-[10px]">close</span> DISMISS
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
};
  
  export default SpatialAnalytics;
