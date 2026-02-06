import { DrumPad } from "./components/Pad";
import "./styles/index.css";
import { useState, useEffect } from "react";

function App() {
  const [activePads, setActivePads] = useState<Map<number, number>>(new Map());
  const [alwaysOnTop, setAlwaysOnTop] = useState(false);

  useEffect(() => {
    const handlePadPress = (e: CustomEvent) => {
      const { index, velocity } = e.detail;
      setActivePads(prev => new Map(prev).set(index, velocity));
    };

    const handlePadRelease = (e: CustomEvent) => {
      const { index } = e.detail;
      setActivePads(prev => {
        const next = new Map(prev);
        next.delete(index);
        return next;
      });
    };

    const handleFocus = () => {
      (window as any).pywebview?.api?.set_window_focus(true);
    };

    const handleBlur = () => {
      (window as any).pywebview?.api?.set_window_focus(false);
    };

    window.addEventListener('padPress', handlePadPress as EventListener);
    window.addEventListener('padRelease', handlePadRelease as EventListener);
    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);
    
    handleFocus();

    return () => {
      window.removeEventListener('padPress', handlePadPress as EventListener);
      window.removeEventListener('padRelease', handlePadRelease as EventListener);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  const toggleAlwaysOnTop = async () => {
    const newState = !alwaysOnTop;
    setAlwaysOnTop(newState);
    try {
      await (window as any).pywebview.api.set_always_on_top(newState);
    } catch (e) {
      console.error('Failed to set always on top:', e);
    }
  };

  return (
    <div className="p-4 flex flex-col items-center">
      <div className="flex gap-4 items-center mb-4">
        <div className="text-gray-500 text-xs">Keyboard input only when focused</div>
        <button
          onClick={toggleAlwaysOnTop}
          className={`px-3 py-1 rounded text-xs ${
            alwaysOnTop 
              ? 'bg-blue-600 hover:bg-blue-700' 
              : 'bg-gray-700 hover:bg-gray-600'
          } text-white`}
        >
          {alwaysOnTop ? '📌 Always on Top' : 'Pin Window'}
        </button>
      </div>
      <div className="grid grid-cols-4 gap-x-4 gap-y-1">
        {Array.from({ length: 16 }, (_, i) => (
          <DrumPad 
            key={i} 
            index={i} 
            isActive={activePads.has(i)} 
            velocity={activePads.get(i) || 0}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
