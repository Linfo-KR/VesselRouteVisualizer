import React from 'react';

const InfoOverlay = ({ route }) => {
  if (!route) return null;

  return (
    <>
      {/* Top Left: Route Info Panel */}
      <div className="absolute top-4 left-14 z-[1000] bg-white shadow-lg rounded-lg overflow-hidden border border-gray-300 max-w-2xl animate-fade-in">
        {/* Header */}
        <div className="bg-[#003399] text-white px-4 py-2 flex justify-between items-center">
          <h2 className="text-lg font-bold">{route.route_name || route.svc || 'Service Route'}</h2>
          <span className="text-xs bg-white text-[#003399] px-2 py-1 rounded font-bold">{route.svc}</span>
        </div>
        
        {/* Info Grid */}
        <div className="grid grid-cols-4 divide-x divide-gray-200 border-b border-gray-200 bg-gray-50 text-center text-xs font-bold text-[#002060]">
          <div className="py-2">Carriers</div>
          <div className="py-2">Duration</div>
          <div className="py-2">Frequency</div>
          <div className="py-2">Ships</div>
        </div>
        <div className="grid grid-cols-4 divide-x divide-gray-200 text-center text-sm text-gray-800">
          <div className="py-2 px-1 truncate" title={route.carriers}>{route.carriers || '-'}</div>
          <div className="py-2 px-1">{route.duration ? `${route.duration} days` : '-'}</div>
          <div className="py-2 px-1">{route.frequency || '-'}</div>
          <div className="py-2 px-1 truncate" title={route.ships}>{route.ships || '-'}</div>
        </div>
        
        {/* Rotation */}
        <div className="bg-gray-50 px-3 py-1 text-xs font-bold text-[#002060] border-b border-gray-200">
            Rotation
        </div>
        <div className="px-3 py-2 text-xs text-gray-700 break-words leading-relaxed max-h-24 overflow-y-auto">
            {route.port_rotation}
        </div>
      </div>

      {/* Top Right: Port Detail Panel (List View) */}
      {route.proforma && route.proforma.length > 0 && (
        <div className="absolute top-4 right-4 z-[1000] bg-white shadow-lg rounded-lg overflow-hidden border border-gray-300 w-72 animate-fade-in max-h-[80vh] overflow-y-auto">
            <div className="bg-[#002570] text-white px-3 py-2 text-center font-bold text-sm sticky top-0 z-10">
                Busan Port Schedule ({route.proforma.length})
            </div>
            <div className="divide-y divide-gray-200">
                {route.proforma.map((pf, idx) => (
                    <div key={idx} className="p-3 text-sm">
                        <div className="flex justify-between items-center mb-1">
                            <span className="font-bold text-[#003399]">{pf.terminal_name}</span>
                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">Seq: {pf.seq}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                                <span className="text-gray-500 block">Weekly T/P</span>
                                <span className="font-medium">{pf.wtp || '-'}</span>
                            </div>
                            <div>
                                <span className="text-gray-500 block">Schedule</span>
                                <span className="font-medium">{pf.sch || '-'}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
      )}
    </>
  );
};

export default InfoOverlay;