import { useState } from "react";
import segmentsData from "./data/segments.json";
import Timeline from "./components/Timeline";
import "./App.css";

function App() {
  const [segments] = useState(segmentsData);
  const [selectedSegment, setSelectedSegment] = useState(
    segmentsData[0] || null
  );

  if (!segments.length) {
    return (
      <div className="app">
        <h1>Podcast Visualization</h1>
        <p>No segments available.</p>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>Podcast Visualization</h1>

      <Timeline
        segments={segments}
        selectedSegment={selectedSegment}
        onSelect={setSelectedSegment}
      />

      {selectedSegment && (
        <div className="details">
          <h2>{selectedSegment.title}</h2>

          <p>
            <strong>Summary:</strong> {selectedSegment.summary}
          </p>

          <p>
            <strong>Keywords:</strong>{" "}
            {selectedSegment.keywords.join(", ")}
          </p>

          <p>
            <strong>Sentiment:</strong>{" "}
            {selectedSegment.sentiment.label} (
            {selectedSegment.sentiment.score})
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
