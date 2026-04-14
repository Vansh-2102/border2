import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import SurveillanceDashboard from './pages/SurveillanceDashboard';
import SnapshotGallery from './pages/SnapshotGallery';
import CameraCalibration from './pages/CameraCalibration';
import SpatialAnalytics from './pages/SpatialAnalytics';

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1c1b1d',
            color: '#e5e1e4',
            borderLeft: '4px solid #c00100',
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: '12px',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            borderRadius: '0px',
          },
          success: {
            style: { borderLeft: '4px solid #4edea3' },
            iconTheme: { primary: '#4edea3', secondary: '#131315' },
          },
          error: {
            style: { borderLeft: '4px solid #c00100' },
            iconTheme: { primary: '#c00100', secondary: '#131315' },
          },
        }}
      />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<SurveillanceDashboard />} />
            <Route path="analytics" element={<SpatialAnalytics />} />
            <Route path="calibration" element={<CameraCalibration />} />
            <Route path="gallery" element={<SnapshotGallery />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
