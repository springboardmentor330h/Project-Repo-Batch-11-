import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  ChevronRight,
  Mic2,
  Clock,
  Hash,
  Menu,
  X,
  AudioLines,
  PlayCircle
} from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const App = () => {
  const [podcasts, setPodcasts] = useState([]);
  const [selectedPodcastId, setSelectedPodcastId] = useState(null);
  const [segments, setSegments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentSegmentId, setCurrentSegmentId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);

  const transcriptRef = useRef(null);

  useEffect(() => {
    fetchPodcasts();
  }, []);

  const fetchPodcasts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/podcasts`);
      setPodcasts(res.data);
    } catch (err) {
      console.error('Error fetching podcasts:', err);
    }
  };

  const fetchPodcastDetails = async (id) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/podcast/${id}`);
      setSegments(res.data);
      setSelectedPodcastId(id);
      setCurrentSegmentId(1);
    } catch (err) {
      console.error('Error fetching podcast details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await axios.get(`${API_BASE}/search`, { params: { q: query } });
      setSearchResults(res.data);
    } catch (err) {
      console.error('Error searching:', err);
    }
  };

  const scrollToSegment = (id) => {
    setCurrentSegmentId(id);
    const element = document.getElementById(`segment-${id}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground font-sans">
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            className="w-80 h-full glass-nav flex-shrink-0 z-50 flex flex-col p-6 overflow-y-auto"
          >
            <div className="flex items-center gap-3 mb-10">
              <div className="p-2 bg-primary/20 rounded-xl">
                <AudioLines className="text-primary" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight">Lexara</h1>
                <p className="text-[10px] text-accent font-medium leading-none mt-1">AI that understands conversations</p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xs font-semibold text-accent uppercase tracking-widest mb-4 px-2">Library</h3>
                <div className="space-y-2">
                  {podcasts.map((pod) => (
                    <button
                      key={pod.id}
                      onClick={() => fetchPodcastDetails(pod.id)}
                      className={`w-full text-left p-3 rounded-xl transition-all flex items-center gap-3 group ${selectedPodcastId === pod.id
                        ? 'bg-primary text-white shadow-lg shadow-primary/20'
                        : 'hover:bg-secondary text-accent hover:text-foreground'
                        }`}
                    >
                      <Mic2 size={18} className={selectedPodcastId === pod.id ? 'text-white' : 'text-primary group-hover:scale-110 transition-transform'} />
                      <span className="text-sm font-medium truncate">{pod.title}</span>
                    </button>
                  ))}
                </div>
              </div>

              {segments.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h3 className="text-xs font-semibold text-accent uppercase tracking-widest mb-4 px-2">Chapters</h3>
                  <div className="space-y-1">
                    {segments.map((seg) => (
                      <button
                        key={seg.segment_id}
                        onClick={() => scrollToSegment(seg.segment_id)}
                        className={`w-full text-left p-2 rounded-lg text-sm transition-all flex items-start gap-2 group ${currentSegmentId === seg.segment_id
                          ? 'bg-secondary text-primary border-l-2 border-primary pl-3'
                          : 'text-accent hover:text-foreground hover:bg-secondary/50'
                          }`}
                      >
                        <span className="mt-1 flex-shrink-0 text-[10px] font-mono opacity-50">#{seg.segment_id}</span>
                        <div className="flex flex-col gap-0.5">
                          <span className="font-bold text-xs line-clamp-1 group-hover:text-primary transition-colors">{seg.title}</span>
                          <span className="text-[10px] opacity-60 line-clamp-1">{seg.summary}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 h-full overflow-hidden flex flex-col relative">
        {/* Top Navbar */}
        <header className="h-20 glass-nav flex items-center justify-between px-8 z-40">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-secondary rounded-xl transition-colors text-accent"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div className="relative group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-accent group-focus-within:text-primary transition-colors" size={18} />
              <input
                type="text"
                placeholder="Search keywords, topics..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="bg-secondary/50 border border-white/5 rounded-xl pl-10 pr-4 py-2 w-80 text-sm focus:outline-none focus:border-primary/50 transition-all focus:w-96"
              />

              {/* Search Results Dropdown */}
              <AnimatePresence>
                {searchResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full left-0 mt-2 w-full glass-card p-2 shadow-2xl max-h-[400px] overflow-y-auto z-50"
                  >
                    {searchResults.map((res, idx) => (
                      <button
                        key={`${res.podcast_id}-${res.segment_id}-${idx}`}
                        className="w-full text-left p-3 hover:bg-secondary rounded-xl transition-colors mb-1 group"
                        onClick={() => {
                          fetchPodcastDetails(res.podcast_id);
                          setSearchResults([]);
                          setSearchQuery('');
                          // Wait for load then scroll
                          setTimeout(() => scrollToSegment(res.segment_id), 500);
                        }}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-bold text-primary uppercase">Pod {res.podcast_id} Seg {res.segment_id}</span>
                          <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <p className="text-xs text-foreground line-clamp-1 font-medium">{res.summary}</p>
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary/50 rounded-full border border-white/5">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-accent">Analyzer Active</span>
            </div>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-12 custom-scrollbar" ref={transcriptRef}>
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center gap-4">
              <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
              <p className="text-accent font-medium animate-pulse">Analyzing segments...</p>
            </div>
          ) : selectedPodcastId ? (
            <div className="max-w-4xl mx-auto space-y-16">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-12"
              >
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full text-primary text-[10px] font-bold uppercase tracking-wider mb-4 border border-primary/20">
                  <PlayCircle size={12} />
                  Live Episode
                </div>
                <h2 className="text-4xl font-extrabold mb-6 tracking-tight">
                  {podcasts.find(p => p.id === selectedPodcastId)?.title}
                </h2>
                <div className="flex flex-wrap gap-2">
                  {segments.reduce((acc, s) => [...acc, ...s.keywords], []).slice(0, 8).map((kw, i) => (
                    <span key={i} className="text-[11px] font-medium bg-secondary text-accent px-3 py-1 rounded-full border border-white/5">
                      #{kw}
                    </span>
                  ))}
                </div>
              </motion.div>

              {segments.map((seg) => (
                <motion.section
                  key={seg.segment_id}
                  id={`segment-${seg.segment_id}`}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-10% 0px -10% 0px' }}
                  className={`group relative p-8 glass-card transition-all duration-500 ${currentSegmentId === seg.segment_id ? 'ring-2 ring-primary/40 bg-secondary/70' : 'hover:bg-secondary/40'
                    }`}
                  onMouseEnter={() => setCurrentSegmentId(seg.segment_id)}
                >
                  <div className="absolute -left-12 top-8 opacity-0 group-hover:opacity-100 transition-all text-primary">
                    <Hash size={24} />
                  </div>

                  <div className="flex flex-col gap-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl font-black text-primary/20">{seg.segment_id < 10 ? `0${seg.segment_id}` : seg.segment_id}</span>
                        <div className="h-4 w-px bg-white/10" />
                        <h3 className="text-xl font-bold tracking-tight text-primary/90">{seg.title}</h3>
                      </div>
                      <div className="flex items-center gap-2 text-accent">
                        <Clock size={14} />
                        <span className="text-xs font-mono">Chapter ID: {seg.segment_id}</span>
                      </div>
                    </div>

                    <p className="text-lg leading-relaxed text-foreground/90 font-medium">
                      {seg.summary}
                    </p>

                    <div className="space-y-4">
                      <div className="h-px w-full bg-white/5" />
                      <div className="flex items-center gap-2">
                        {seg.keywords.map((kw, idx) => (
                          <span key={idx} className="text-[10px] font-bold text-primary/80 bg-primary/5 px-2 py-0.5 rounded border border-primary/10">
                            {kw}
                          </span>
                        ))}
                      </div>
                      <p className="text-sm text-accent leading-loose text-justify opacity-80 group-hover:opacity-100 transition-opacity">
                        {seg.text}
                      </p>
                    </div>
                  </div>
                </motion.section>
              ))}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                className="w-24 h-24 bg-primary/10 rounded-3xl flex items-center justify-center mb-8 border border-primary/20"
              >
                <AudioLines size={48} className="text-primary" />
              </motion.div>
              <h2 className="text-3xl font-bold mb-4 tracking-tight">Welcome to Lexara</h2>
              <p className="text-accent max-w-md mx-auto leading-relaxed">
                Experience AI that understands conversations. Select an episode from the library to explore deep-segmented podcast intelligence.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
