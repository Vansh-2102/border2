const API_BASE_URL = 'http://localhost:8000';

export const mockLoadingDelay = async (ms = 500) => {
    return new Promise(resolve => setTimeout(resolve, ms));
};

// ----------------------------------------------------
// CAMERA CALIBRATION API
// ----------------------------------------------------
export const setCameraCalibration = async (coordinates) => {
    const response = await fetch(`${API_BASE_URL}/calibrate_camera`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(coordinates),
    });
    if (!response.ok) throw new Error('Calibration failed');
    return response.json();
};

// ----------------------------------------------------
// SURVEILLANCE DASHBOARD API
// ----------------------------------------------------
export const toggleNightVisionCam = async (isEnabled) => {
    const response = await fetch(`${API_BASE_URL}/toggle_night_vision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: isEnabled }),
    });
    if (!response.ok) throw new Error('Failed to toggle night vision');
    return response.json();
};

export const startLiveStream = async () => {
    // This is mostly a UI trigger for now as the stream is MJPEG
    return { success: true };
};

// ----------------------------------------------------
// ANALYTICS & LOG API
// ----------------------------------------------------
export const deployDroneToTarget = async (targetId) => {
    const response = await fetch(`${API_BASE_URL}/deploy_drone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_id: targetId }),
    });
    if (!response.ok) throw new Error('Drone deployment failed');
    return response.json();
};

export const dismissAlert = async (targetId) => {
    const response = await fetch(`${API_BASE_URL}/dismiss_alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_id: targetId }),
    });
    if (!response.ok) throw new Error('Failed to dismiss alert');
    return response.json();
};

// ----------------------------------------------------
// GALLERY API
// ----------------------------------------------------
export const applyGalleryFilters = async (filters) => {
    const response = await fetch(`${API_BASE_URL}/gallery/filter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
    });
    if (!response.ok) return { success: false, itemsFound: 0 };
    return response.json();
};

export const refreshGalleryData = async () => {
    const response = await fetch(`${API_BASE_URL}/gallery/refresh`);
    if (!response.ok) return { success: false };
    return response.json();
};

// ----------------------------------------------------
// SYSTEM API
// ----------------------------------------------------
export const triggerSystemSettings = async () => {
    const response = await fetch(`${API_BASE_URL}/system_settings`);
    if (!response.ok) return { success: false };
    return response.json();
};
