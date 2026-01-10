import { useState, useEffect } from 'react';
import RouteList from './components/RouteList';
import MapVisualizer from './components/MapVisualizer';
import InfoOverlay from './components/InfoOverlay';
import { portService, routeService } from './services/api';

import './App.css';

function App() {
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [routeDetail, setRouteDetail] = useState(null); // Full detail with Proforma
  const [allPorts, setAllPorts] = useState([]);
  const [loadingPorts, setLoadingPorts] = useState(true);
  const [portsError, setPortsError] = useState(null);
  
  // UI State
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    const fetchPorts = async () => {
      try {
        const data = await portService.getAllPorts();
        setAllPorts(data);
      } catch (error) {
        console.error("Failed to fetch ports:", error);
        setPortsError('Failed to load port data');
      } finally {
        setLoadingPorts(false);
      }
    };
    fetchPorts();
  }, []);

  const handleSelectRoute = async (route) => {
    setSelectedRoute(route); // Immediate feedback with basic data
    setRouteDetail(null); // Clear previous detail
    
    try {
        // Fetch full details (including Proforma)
        const id = route.route_idx || route.id;
        const detail = await routeService.getRouteById(id);
        setRouteDetail(detail);
    } catch (e) {
        console.error("Failed to load route detail", e);
        // Fallback to basic route data if detail fetch fails
        setRouteDetail(route);
    }
  };

  if (loadingPorts) {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 flex-col">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600 font-medium">Loading Global Port Database...</p>
        </div>
    );
  }

  if (portsError) {
    return <div className="flex items-center justify-center min-h-screen text-xl text-red-600">{portsError}</div>;
  }

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Sidebar Area */}
      <div 
        className={`transition-all duration-300 ease-in-out border-r border-gray-300 bg-white z-20 flex-shrink-0 ${
            isSidebarCollapsed ? 'w-16' : 'w-80'
        }`}
      >
        <RouteList 
            onSelectRoute={handleSelectRoute} 
            selectedRouteId={selectedRoute?.route_idx || selectedRoute?.id} 
            isCollapsed={isSidebarCollapsed}
            toggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </div>

      {/* Main Map Area */}
      <div className="flex-1 relative">
        <MapVisualizer 
            selectedRoute={selectedRoute} 
            allPorts={allPorts} 
            onRouteUpdated={() => {
                if (selectedRoute) {
                    handleSelectRoute(selectedRoute);
                }
            }}
        />
        
        {/* Info Overlay (Floating on top of map) */}
        {routeDetail && (
            <InfoOverlay route={routeDetail} />
        )}
      </div>
    </div>
  );
}

export default App;
