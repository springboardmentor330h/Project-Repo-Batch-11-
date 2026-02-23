import React from 'react';

/**
 * Timeline Component
 * Renders a horizontal bar representing the podcast segments.
 * Color-coded by sentiment.
 */
const Timeline = ({ segments, currentSegmentId, onSegmentClick }) => {
    if (!segments || segments.length === 0) return null;

    // Map sentiment labels to colors (Purple Dark Theme palette)
    const getSentimentColor = (sentiment) => {
        const label = sentiment?.label || 'Neutral';
        switch (label) {
            case 'Positive': return 'bg-emerald-500/80';
            case 'Negative': return 'bg-rose-500/80';
            default: return 'bg-purple-500/40';
        }
    };

    return (
        <div className="w-full mb-8 pt-4">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-accent/70">Podcast Timeline</h3>
                <span className="text-[10px] text-accent/50">{segments.length} Chapters</span>
            </div>
            <div className="h-3 w-full flex rounded-full overflow-hidden bg-secondary/30 border border-white/5 cursor-pointer">
                {segments.map((segment) => (
                    <div
                        key={segment.segment_id}
                        onClick={() => onSegmentClick(segment.segment_id)}
                        className={`h-full transition-all duration-300 hover:brightness-125 relative group ${getSentimentColor(segment.sentiment)} ${currentSegmentId === segment.segment_id ? 'ring-2 ring-white ring-inset scale-y-125 z-10' : ''
                            }`}
                        style={{ width: `${100 / segments.length}%` }}
                    >
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-2 bg-secondary border border-white/10 rounded-lg text-[10px] opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-2xl">
                            <div className="font-bold text-primary">{segment.title}</div>
                            <div className="text-accent/70">{segment.sentiment?.label || 'Neutral'}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Timeline;
