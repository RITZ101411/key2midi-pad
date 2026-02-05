import { DrumPad } from "./components/Pad";
import "./styles/index.css";
import { useState, useEffect } from "react";

function App() {
  const [activePads, setActivePads] = useState<Set<number>>(new Set());

  useEffect(() => {
    const handlePadPress = (e: CustomEvent) => {
      setActivePads(prev => new Set(prev).add(e.detail));
    };

    const handlePadRelease = (e: CustomEvent) => {
      setActivePads(prev => {
        const next = new Set(prev);
        next.delete(e.detail);
        return next;
      });
    };

    window.addEventListener('padPress', handlePadPress as EventListener);
    window.addEventListener('padRelease', handlePadRelease as EventListener);
    return () => {
      window.removeEventListener('padPress', handlePadPress as EventListener);
      window.removeEventListener('padRelease', handlePadRelease as EventListener);
    };
  }, []);

  return (
    <div className="p-4 flex justify-center">
      <div className="grid grid-cols-4 gap-x-4 gap-y-1">
        {Array.from({ length: 16 }, (_, i) => (
          <DrumPad key={i} index={i} isActive={activePads.has(i)} />
        ))}
      </div>
    </div>
  );
}

export default App;
