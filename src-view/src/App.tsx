function App() {
  return (
    <>
      <div className="top-buttons">
        <div className="top-btn">PAD設定</div>
        <div className="top-btn"></div>
        <div className="top-btn"></div>
        <div className="top-btn"></div>
      </div>
      <div className="grid">
        {Array.from({ length: 16 }, (_, i) => (
          <div key={i} className="container">
            <div className="pad" id={`pad${i}`}></div>
            <div className="label">PAD{i + 1}</div>
          </div>
        ))}
      </div>
    </>
  )
}

export default App
