import { useState } from 'react';
import toast from 'react-hot-toast';
import { setCameraCalibration } from '../api/apiClient';

const CameraCalibration = () => {
    const defaultCoords = {
      P1_X: "1242.04", P1_Y: "432.88",
      P2_X: "2601.12", P2_Y: "430.55",
      P3_X: "3120.90", P3_Y: "1840.21",
      P4_X: "722.33",  P4_Y: "1839.99"
    };

    const [coords, setCoords] = useState(defaultCoords);
    const [isCalibrating, setIsCalibrating] = useState(false);

    const handleInputChange = (e) => {
        setCoords({
            ...coords,
            [e.target.name]: e.target.value
        });
    };

    const handleReset = () => {
        setCoords(defaultCoords);
        toast('Reference coordinates reset to default.', { icon: '🔄' });
    };

    const handleCalibration = async () => {
        setIsCalibrating(true);
        toast.loading('Processing homography matrix projection...', { id: 'calib' });
        
        try {
            const response = await setCameraCalibration(coords);
            toast.success(response.message, { id: 'calib' });
        } catch (error) {
            toast.error('Calibration failed. Check inputs.', { id: 'calib' });
        } finally {
            setIsCalibrating(false);
        }
    };

    return (
      <div className="flex-1 p-8 overflow-y-auto bg-surface relative">
        <div className="absolute inset-0 scanline pointer-events-none opacity-20"></div>
        {/* Header Section */}
        <div className="mb-8 flex justify-between items-end">
          <div>
            <h1 className="font-headline text-3xl font-black tracking-tighter uppercase text-on-surface">Camera Calibration <span className="text-[#c00100]">_V4.2</span></h1>
            <p className="font-label text-[10px] tracking-[0.2em] text-zinc-500 uppercase mt-1">Status: Manual Geometry Override Active</p>
          </div>
          <div className="flex gap-4">
            <button onClick={handleReset} className="bg-surface-container-high px-4 py-2 text-[10px] font-headline font-bold uppercase tracking-widest border-l-2 border-[#ffbf00] flex items-center gap-2 hover:bg-surface-container-highest transition-colors active:scale-95">
              <span className="material-symbols-outlined text-sm">refresh</span> Reset Reference
            </button>
            <button 
                onClick={handleCalibration} 
                disabled={isCalibrating}
                className={`px-6 py-2 text-[10px] font-headline font-bold uppercase tracking-widest text-white flex items-center gap-2 transition-all active:scale-95 ${
                    isCalibrating ? 'bg-zinc-700 cursor-wait' : 'bg-[#c00100] hover:opacity-90'
                }`}
            >
              <span className="material-symbols-outlined text-sm">{isCalibrating ? 'hourglass_top' : 'precision_manufacturing'}</span> 
              {isCalibrating ? 'Processing...' : 'Set Calibration'}
            </button>
          </div>
        </div>
        
        {/* Bento Grid Layout */}
        <div className="grid grid-cols-12 gap-6">
          {/* Primary Calibration Viewport */}
          <div className="col-span-12 lg:col-span-8 bg-surface-container relative aspect-video group border border-outline-variant/10 shadow-2xl">
            <div className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur-md p-2 border border-outline-variant/20">
              <div className="font-headline text-[9px] font-bold text-[#4edea3] tracking-[0.3em] uppercase">Ref_Source: Cam_08_North</div>
            </div>
            {/* Reference Image */}
            <img alt="Tactical Surveillance View" className="w-full h-full object-cover grayscale opacity-60" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAm_wnio6t00IMz1cEru3JYlVzcDX7sAxHtys1PUSCh0Lktkw7ZR83728SVGGA-AvYl4eFV-UkN4g-ZFOrl59dvQ6gNoPzpxKiKB7hbk_G4OpXrF5lSjLF-RIVkyUDD7uvunMbfT_Nu0skT9fuo8USLDPzS1OaSpFmHNLwDcqyNuTADCj02Bdm_kHx3rmmnSpuNjl3N4De-WWTYAwysGcgZ7A6xuRDOw-jhLrviPgIhUkqavJNs8jJKtMkEVodjbwesqYZdeO4F39c"/>
            {/* Calibration Overlay Layer */}
            <div className={`absolute inset-0 p-12 transition-opacity duration-1000 ${isCalibrating ? 'opacity-20' : 'opacity-100'}`}>
              <div className="w-full h-full border-[1px] border-dashed border-[#4edea3]/30 relative">
                {/* Perspective Grid */}
                <div className="absolute inset-x-0 bottom-0 h-1/2 opacity-40" style={{
                  backgroundImage: "linear-gradient(rgba(78, 222, 163, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(78, 222, 163, 0.1) 1px, transparent 1px)",
                  backgroundSize: "40px 40px",
                  transform: "perspective(500px) rotateX(60deg)"
                }}></div>
                {/* Calibration Points */}
                {/* Point 1 */}
                <div className="absolute top-[20%] left-[25%] -translate-x-1/2 -translate-y-1/2 group/point hover:z-50">
                  <div className="w-10 h-10 border border-[#c00100] flex items-center justify-center relative hover:bg-[#c00100]/20 cursor-move transition-colors">
                    <div className="w-1 h-1 bg-[#c00100]"></div>
                    <div className="absolute -top-6 left-0 bg-[#c00100] text-white text-[8px] px-1 font-headline font-bold">PT_01</div>
                    <div className="absolute w-20 h-20 border border-[#c00100]/20 scale-0 group-hover/point:scale-100 transition-transform pointer-events-none"></div>
                  </div>
                </div>
                {/* Point 2 */}
                <div className="absolute top-[20%] right-[25%] translate-x-1/2 -translate-y-1/2">
                  <div className="w-10 h-10 border border-[#c00100] flex items-center justify-center relative hover:bg-[#c00100]/20 cursor-move transition-colors">
                    <div className="w-1 h-1 bg-[#c00100]"></div>
                    <div className="absolute -top-6 left-0 bg-[#c00100] text-white text-[8px] px-1 font-headline font-bold">PT_02</div>
                  </div>
                </div>
                {/* Point 3 */}
                <div className="absolute bottom-[15%] right-[10%] translate-x-1/2 translate-y-1/2">
                  <div className="w-10 h-10 border border-[#c00100] flex items-center justify-center relative hover:bg-[#c00100]/20 cursor-move transition-colors">
                    <div className="w-1 h-1 bg-[#c00100]"></div>
                    <div className="absolute -bottom-6 left-0 bg-[#c00100] text-white text-[8px] px-1 font-headline font-bold">PT_03</div>
                  </div>
                </div>
                {/* Point 4 */}
                <div className="absolute bottom-[15%] left-[10%] -translate-x-1/2 translate-y-1/2">
                  <div className="w-10 h-10 border border-[#c00100] flex items-center justify-center relative hover:bg-[#c00100]/20 cursor-move transition-colors">
                    <div className="w-1 h-1 bg-[#c00100]"></div>
                    <div className="absolute -bottom-6 left-0 bg-[#c00100] text-white text-[8px] px-1 font-headline font-bold">PT_04</div>
                  </div>
                </div>
                {/* Connecting Perspective Box */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" viewBox="0 0 100 100">
                  <polygon fill="rgba(192, 1, 0, 0.05)" points="25,20 75,20 90,85 10,85" stroke="#c00100" strokeWidth="0.2"></polygon>
                </svg>
              </div>
            </div>
            
            {isCalibrating && (
                <div className="absolute inset-0 flex items-center justify-center z-20">
                    <div className="bg-black/80 backdrop-blur-md p-6 border border-[#c00100]/50 tracking-[0.2em] uppercase text-[#c00100] font-headline text-xs font-black animate-pulse flex flex-col items-center">
                        <span className="material-symbols-outlined mb-2 !text-3xl animate-spin">autorenew</span>
                        Computing Matrix...
                    </div>
                </div>
            )}

            <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-md px-3 py-1 border border-outline-variant/20 flex gap-4">
              <span className="text-[9px] font-headline text-zinc-400">RESOLUTION: 3840x2160</span>
              <span className="text-[9px] font-headline text-zinc-400">LAT: 51.5074° N</span>
              <span className="text-[9px] font-headline text-zinc-400">LONG: 0.1278° W</span>
            </div>
          </div>
  
          {/* Tactical Controls Sidebar */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <div className="bg-surface-container p-6 border-l-2 border-outline">
              <h3 className="font-headline text-xs font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-sm text-[#c00100]">grid_4x4</span> Coordinate Entry
              </h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P1_X_COORD</label>
                    <input name="P1_X" value={coords.P1_X} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P1_Y_COORD</label>
                    <input name="P1_Y" value={coords.P1_Y} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P2_X_COORD</label>
                    <input name="P2_X" value={coords.P2_X} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P2_Y_COORD</label>
                    <input name="P2_Y" value={coords.P2_Y} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P3_X_COORD</label>
                    <input name="P3_X" value={coords.P3_X} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P3_Y_COORD</label>
                    <input name="P3_Y" value={coords.P3_Y} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P4_X_COORD</label>
                    <input name="P4_X" value={coords.P4_X} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                  <div className="space-y-1">
                    <label className="font-headline text-[8px] text-zinc-500 uppercase tracking-tighter">P4_Y_COORD</label>
                    <input name="P4_Y" value={coords.P4_Y} onChange={handleInputChange} className="w-full bg-surface-container-high border-none text-xs font-mono p-2 focus:ring-0 outline-none border-l-2 border-outline-variant focus:border-[#c00100] text-[#ffb4a8]" type="text" />
                  </div>
                </div>
              </div>
            </div>
            {/* Spatial Metadata */}
            <div className="bg-surface-container-lowest p-6 border border-outline-variant/10">
              <h3 className="font-headline text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-4">Perspective Analytics</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center"><span className="text-[9px] font-mono text-zinc-400 uppercase">FOV_Horizontal</span><span className="text-[10px] font-mono text-[#4edea3]">104.2°</span></div>
                <div className="flex justify-between items-center"><span className="text-[9px] font-mono text-zinc-400 uppercase">Aspect_Ratio</span><span className="text-[10px] font-mono text-[#4edea3]">1.77:1</span></div>
                <div className="flex justify-between items-center"><span className="text-[9px] font-mono text-zinc-400 uppercase">Ground_Plane_Confidence</span><div className="w-24 h-1 bg-surface-container-high"><div className="w-[92%] h-full bg-[#4edea3]"></div></div><span className="text-[10px] font-mono text-[#4edea3]">92%</span></div>
                <div className="flex justify-between items-center"><span className="text-[9px] font-mono text-zinc-400 uppercase">Radial_Distortion_Correction</span><span className="text-[10px] font-mono text-[#c00100]">ENABLED</span></div>
              </div>
            </div>
            {/* System Diagnostics Log */}
            <div className="bg-[#0e0e10] p-4 font-mono text-[9px] text-zinc-500 leading-relaxed border-t border-[#603e39]/30">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-1.5 h-1.5 rounded-full bg-[#4edea3] ${isCalibrating ? 'animate-pulse' : ''}`}></div>
                <span className="text-[#4edea3]">CALIBRATION_ENGINE_{isCalibrating ? 'ACTIVE' : 'IDLE'}</span>
              </div>
              <p>&gt; Initializing Homography Matrix computation...</p>
              <p>&gt; Mapping source points to target ground plane...</p>
              <p>&gt; Projection error: 0.042px (Optimal)</p>
              <p>&gt; {isCalibrating ? 'Computing mesh...' : 'Grid mesh projected. Waiting for user confirmation.'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  export default CameraCalibration;
