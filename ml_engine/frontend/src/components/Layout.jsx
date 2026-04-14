import { Link, Outlet, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { triggerSystemSettings } from '../api/apiClient';

const Layout = () => {
  const location = useLocation();

  const getLinkClasses = (path) => {
    const isActive = location.pathname === path;
    if (isActive) {
      return "font-['Space_Grotesk'] uppercase tracking-[0.05em] text-xs font-bold text-[#c00100] border-b-2 border-[#c00100] pb-2";
    }
    return "font-['Space_Grotesk'] uppercase tracking-[0.05em] text-xs font-bold text-zinc-500 hover:text-zinc-200 transition-colors cursor-pointer";
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      const query = e.target.value;
      toast(`Searching database for: ${query}...`);
      e.target.value = '';
    }
  };

  const handleFeatureClick = (featureName) => {
    toast.error(`Feature '${featureName}' is currently disconnected from backend.`);
  };

  const handleSettingsClick = async () => {
    toast.loading('Accessing secure settings...', { id: 'settings' });
    await triggerSystemSettings();
    toast.success('Settings initialized.', { id: 'settings' });
  };

  return (
    <>
      <header className="bg-[#0e0e10] border-b-[0.5px] border-[#603e39]/15 w-full sticky top-0 z-50 shadow-none flex justify-between items-center px-6 py-3">
        <div className="flex items-center gap-8">
          <span className="font-['Space_Grotesk'] text-lg font-black text-[#c00100] tracking-tighter">SENTINEL SPATIAL AI</span>
          <nav className="hidden md:flex gap-6">
            <Link className={getLinkClasses('/')} to="/">Surveillance</Link>
            <Link className={getLinkClasses('/analytics')} to="/analytics">Analytics</Link>
            <Link className={getLinkClasses('/calibration')} to="/calibration">Calibration</Link>
            <Link className={getLinkClasses('/gallery')} to="/gallery">Gallery</Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <div className="bg-surface-container px-3 py-1 border-l-2 border-outline-variant/30 flex items-center gap-2">
            <span className="material-symbols-outlined text-[16px] text-zinc-500">search</span>
            <input 
              className="bg-transparent border-none text-[10px] font-headline tracking-widest text-on-surface focus:outline-none focus:ring-0 outline-none placeholder:text-zinc-600 uppercase w-32" 
              placeholder="QUERY_ID (ENTER)..." 
              type="text"
              onKeyDown={handleSearch}
            />
          </div>
          <button onClick={handleSettingsClick} className="material-symbols-outlined text-zinc-400 hover:text-zinc-200 transition-all active:scale-95">settings</button>
          <button onClick={() => toast('Profile details secured.')} className="material-symbols-outlined text-zinc-400 hover:text-zinc-200 transition-all active:scale-95">account_circle</button>
        </div>
      </header>

      <div className="flex h-[calc(100vh-104px)]">
        <aside className="bg-[#131315] border-r-[0.5px] border-[#603e39]/15 h-screen w-64 fixed left-0 top-0 shadow-[20px_0_40px_rgba(0,0,0,0.4)] flex flex-col pt-16 z-40">
          <div className="px-6 py-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-surface-container-highest flex items-center justify-center border border-outline-variant/20">
                <span className="material-symbols-outlined text-inverse-primary" style={{fontVariationSettings: "'FILL' 1"}}>admin_panel_settings</span>
              </div>
              <div>
                <div className="font-['Space_Grotesk'] text-[10px] tracking-widest uppercase text-on-surface font-bold">OPERATOR_01</div>
                <div className="font-['Space_Grotesk'] text-[8px] tracking-widest uppercase text-zinc-500">SECTOR: NORTH_GRID</div>
              </div>
            </div>
          </div>
          <nav className="flex-1">
            <Link className="flex items-center gap-4 py-3 bg-[#201f22] text-[#c00100] border-l-4 border-[#c00100] pl-4 font-['Space_Grotesk'] text-[10px] tracking-widest uppercase" to="/">
              <span className="material-symbols-outlined">radar</span> Live View
            </Link>
            <button onClick={() => handleFeatureClick('Object Detection')} className="w-full flex items-center gap-4 py-3 text-zinc-400 pl-5 hover:bg-white/5 hover:text-white transition-all font-['Space_Grotesk'] text-[10px] tracking-widest uppercase">
              <span className="material-symbols-outlined">visibility</span> Object Detection
            </button>
            <button onClick={() => handleFeatureClick('Thermal Grid')} className="w-full flex items-center gap-4 py-3 text-zinc-400 pl-5 hover:bg-white/5 hover:text-white transition-all font-['Space_Grotesk'] text-[10px] tracking-widest uppercase">
              <span className="material-symbols-outlined">thermostat</span> Thermal Grid
            </button>
            <button onClick={() => handleFeatureClick('Signal Intel')} className="w-full flex items-center gap-4 py-3 text-zinc-400 pl-5 hover:bg-white/5 hover:text-white transition-all font-['Space_Grotesk'] text-[10px] tracking-widest uppercase">
              <span className="material-symbols-outlined">wifi_tethering_error</span> Signal Intel
            </button>
          </nav>
          <div className="pb-24 border-t border-outline-variant/10">
            <button onClick={handleSettingsClick} className="w-full flex items-center gap-4 py-3 text-zinc-400 pl-5 hover:bg-white/5 hover:text-white transition-all font-['Space_Grotesk'] text-[10px] tracking-widest uppercase">
              <span className="material-symbols-outlined">settings_suggest</span> System Settings
            </button>
            <button onClick={() => toast('Session disconnected.')} className="w-full flex items-center gap-4 py-3 text-zinc-400 pl-5 hover:bg-white/5 hover:text-white transition-all font-['Space_Grotesk'] text-[10px] tracking-widest uppercase">
              <span className="material-symbols-outlined">logout</span> Logout
            </button>
          </div>
        </aside>

        <main className="ml-64 flex-1 flex flex-col overflow-hidden relative">
          <Outlet />
        </main>
      </div>

      <div className="bg-[#0e0e10] border-t-[0.5px] border-[#603e39]/15 fixed bottom-0 w-full z-50 flex justify-between items-center px-4 py-1.5 h-8">
        <div className="flex items-center gap-6">
          <span className="font-['Inter'] text-[9px] font-mono tracking-tighter text-[#4edea3] font-bold">FPS: 120 | GPU_LOAD: 42% | LATENCY: 14MS | SYSTEM_READY</span>
          <div className="flex items-center gap-3">
            <span className="font-['Inter'] text-[9px] font-mono tracking-tighter text-zinc-600 hover:text-[#4edea3] cursor-help transition-all">Diagnostics</span>
            <span className="font-['Inter'] text-[9px] font-mono tracking-tighter text-zinc-600 hover:text-[#4edea3] cursor-help transition-all">Network Status</span>
            <span className="font-['Inter'] text-[9px] font-mono tracking-tighter text-zinc-600 hover:text-[#4edea3] cursor-help transition-all">Encryption: AES-256</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-[9px] font-mono text-zinc-500 uppercase">
          <span>{new Date().toLocaleTimeString('en-US', { hour12: false })} UTC</span>
          <span className="w-2 h-2 bg-tertiary-container rounded-full shadow-[0_0_5px_#4edea3]"></span>
        </div>
      </div>
    </>
  );
};

export default Layout;
