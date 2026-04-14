import { useState } from 'react';
import toast from 'react-hot-toast';
import { applyGalleryFilters, refreshGalleryData } from '../api/apiClient';

const SnapshotGallery = () => {

    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isFiltering, setIsFiltering] = useState(false);
    const [items, setItems] = useState([]);
    
    // UI state for dropdown tags (just decorative pseudo-state to show interactiveness)
    const [filterThreat, setFilterThreat] = useState('CRITICAL');

    const handleApplyFilters = async () => {
        setIsFiltering(true);
        toast.loading('Applying threat classification filters...', { id: 'filter' });
        try {
            const res = await applyGalleryFilters({ threat: filterThreat === 'CRITICAL' ? 'HIGH' : 'ALL' });
            if (res.success) {
                setItems(res.items || []);
                toast.success(`Filters Applied: ${res.itemsFound} items matched.`, { id: 'filter' });
            }
        } catch (e) {
            toast.error('Search query failed.', { id: 'filter' });
        } finally {
            setIsFiltering(false);
        }
    };

    const handleRefresh = async () => {
        setIsRefreshing(true);
        toast.loading('Syncing latest intercepts from data lake...', { id: 'refresh' });
        try {
            const res = await refreshGalleryData();
            if (res.success) {
                setItems(res.items || []);
                toast.success('Gallery synchronized.', { id: 'refresh' });
            }
        } catch (e) {
            toast.error('Sync failed.', { id: 'refresh' });
        } finally {
            setIsRefreshing(false);
        }
    };

    const handleCardClick = (id) => {
        toast(`Archive Log ID: ${id} mapped to clipboard.`, { icon: '📋' });
    };

    return (
      <div className="flex-grow pt-6 pb-20 px-6 min-h-full overflow-y-auto">
        <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="font-headline text-3xl font-black tracking-tighter text-on-surface">SNAPSHOT_GALLERY</h1>
            <p className="font-mono text-[10px] text-zinc-500 uppercase tracking-widest mt-1 flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-inverse-primary animate-pulse"></span>
              ACTIVE ARCHIVE // SECTOR_NORTH_01
            </p>
          </div>
          <div className="flex flex-wrap gap-2 items-center bg-surface-container-lowest p-1">
            <div className="px-3 py-1.5 bg-surface-container-high flex items-center gap-2 border-l-2 border-outline-variant cursor-not-allowed opacity-50">
              <span className="material-symbols-outlined text-xs text-zinc-500">calendar_today</span>
              <span className="font-label text-[10px] uppercase tracking-wider text-on-surface">DATE: ALL</span>
            </div>
            <div 
                onClick={() => setFilterThreat(filterThreat === 'CRITICAL' ? 'ALL' : 'CRITICAL')} 
                className="px-3 py-1.5 bg-surface-container-high flex items-center gap-2 border-l-2 border-inverse-primary cursor-pointer hover:bg-white/10 transition-colors"
                title="Toggle Threat Requirement"
            >
              <span className="material-symbols-outlined text-xs text-inverse-primary">warning</span>
              <span className="font-label text-[10px] uppercase tracking-wider text-on-surface">THREAT: {filterThreat}</span>
            </div>
            <div className="px-3 py-1.5 bg-surface-container-high flex items-center gap-2 border-l-2 border-tertiary cursor-not-allowed opacity-50">
              <span className="material-symbols-outlined text-xs text-tertiary">category</span>
              <span className="font-label text-[10px] uppercase tracking-wider text-on-surface">CLASS: UNKNOWN</span>
            </div>
            <button 
                onClick={handleApplyFilters}
                disabled={isFiltering}
                className={`px-4 py-1.5 text-white font-label text-[10px] uppercase tracking-widest transition-all ${isFiltering ? 'bg-zinc-700 animate-pulse' : 'bg-inverse-primary hover:opacity-90 active:scale-95'}`}
            >
              {isFiltering ? 'QUERYING...' : 'APPLY FILTERS'}
            </button>
          </div>
        </header>

        <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-0.5 bg-[#603e39]/10 border-[0.5px] border-[#603e39]/15 ${isRefreshing ? 'opacity-50 pointer-events-none blur-sm transition-all' : 'transition-all duration-500'}`}>
          {items.map(item => (
            <div key={item.id} onClick={() => handleCardClick(item.id)} className="bg-surface-container relative group overflow-hidden kinetic-glow cursor-pointer">
              <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
                <span className={`${item.type === 'HIGH' ? 'bg-inverse-primary' : 'bg-secondary-container text-on-secondary-container'} text-white px-2 py-0.5 text-[8px] font-bold tracking-tighter uppercase`}>
                  {item.type === 'HIGH' ? 'CRITICAL' : item.type}
                </span>
                <span className="bg-black/60 backdrop-blur-md text-white px-2 py-0.5 text-[8px] font-mono tracking-tighter">ID: {item.id}</span>
              </div>
              <div className="aspect-square bg-zinc-900 relative">
                <img className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity grayscale contrast-125" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBpebVy3ru94bW1a7pu566ekNQBqIaHIzVSp3AwQvIuCuymGOvf5gSSC0Ijp4Zj8IPGcqtIcjzalI9TZZ1Z_D9siD_EGXU5vTfDssFZqocmh02BP-Hpodc2lp7ltFQrvCrB7XPO7RxM9Nnghpwr5Allqij5ZKw__pHprqaAzYUOYN5JbG06BuWLNIeGUkHUNoIvzS6sER3u4b_ZmLmUMsnpAPjWdjTvwZkrEzegBLI-2-ZhNvDZlcA9IpKLkI-SxDtFkiAtmvE6b2o" alt="Gallery item" />
                <div className="absolute inset-0 scanline pointer-events-none"></div>
                <div className="absolute bottom-2 right-2">
                  <span className="material-symbols-outlined text-inverse-primary text-sm">center_focus_strong</span>
                </div>
              </div>
              <div className="p-4 border-t border-[#603e39]/10">
                <div className="flex justify-between items-start mb-2">
                  <div className="font-headline text-xs font-bold tracking-tight">{item.class_name}_DETECTION</div>
                  <div className="font-mono text-[9px] text-zinc-500">{item.timestamp} // {item.date}</div>
                </div>
                <div className="flex gap-4">
                  <div className="flex flex-col"><span className="text-[8px] text-zinc-600 uppercase tracking-widest">Distance</span><span className="text-[10px] font-mono text-zinc-300">{item.distance}m</span></div>
                  <div className="flex flex-col"><span className="text-[8px] text-zinc-600 uppercase tracking-widest">Confidence</span><span className="text-[10px] font-mono text-tertiary">{Math.round(item.confidence * 100)}%</span></div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Empty Refresh Card */}
          <div onClick={handleRefresh} className="bg-surface-container-low flex flex-col items-center justify-center border-dashed border-2 border-[#603e39]/20 p-8 min-h-[300px] cursor-pointer hover:bg-white/5 transition-all group">
            <span className={`material-symbols-outlined text-3xl mb-4 transition-colors ${isRefreshing ? 'text-[#c00100] animate-spin' : 'text-zinc-700 group-hover:text-white'}`}>refresh</span>
            <span className="font-headline text-[10px] text-zinc-500 uppercase tracking-widest group-hover:text-zinc-300">Awaiting New Data...</span>
            <span className="font-mono text-[8px] text-zinc-700 mt-2">CLICK TO REFRESH</span>
          </div>
        </div>
      </div>
    );
  };
  
  export default SnapshotGallery;
