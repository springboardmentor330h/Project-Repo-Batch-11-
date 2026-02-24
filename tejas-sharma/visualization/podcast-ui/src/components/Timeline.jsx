import "./Timeline.css";

function Timeline({ segments, selectedSegment, onSelect }) {
  const totalDuration = segments[segments.length - 1].end_time;

  return (
    <div className="timeline">
      {segments.map((segment) => {
        const duration = segment.end_time - segment.start_time;
        const widthPercent = (duration / totalDuration) * 100;

        return (
          <div
            key={segment.id}
            className={`timeline-segment ${
              selectedSegment.id === segment.id ? "active" : ""
            }`}
            style={{ width: `${widthPercent}%` }}
            onClick={() => onSelect(segment)}
            title={segment.title}
          >
            <span className="segment-id">{segment.id}</span>
          </div>
        );
      })}
    </div>
  );
}

export default Timeline;
