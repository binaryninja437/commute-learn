import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Upload, Play, Pause, SkipBack, SkipForward, Volume2, VolumeX,
  Download, Trash2, Clock, BookOpen, Sparkles, Headphones,
  FileText, Image, ChevronRight, Check, Loader2, X, Music,
  Home, Library, Search, Plus, MoreHorizontal, Repeat, Shuffle
} from 'lucide-react';

// API Configuration
const API_BASE = 'https://commute-learn-api.onrender.com/api';

// ============================================
// MAIN APP COMPONENT
// ============================================
export default function App() {
  const [currentView, setCurrentView] = useState('home'); // home, upload, processing, player, library
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [currentPodcast, setCurrentPodcast] = useState(null);
  const [library, setLibrary] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [subject, setSubject] = useState('Physics');
  const [chapter, setChapter] = useState('');
  
  const audioRef = useRef(null);
  const pollIntervalRef = useRef(null);

  // Load library on mount
  useEffect(() => {
    fetchLibrary();
  }, []);

  // Fetch user's podcast library
  const fetchLibrary = async () => {
    try {
      const res = await fetch(`${API_BASE}/library`);
      const data = await res.json();
      setLibrary(data.podcasts || []);
    } catch (err) {
      console.error('Failed to fetch library:', err);
    }
  };

  // Poll for processing status
  const pollStatus = useCallback(async (jid) => {
    try {
      const res = await fetch(`${API_BASE}/status/${jid}`);
      const data = await res.json();
      setProcessingStatus(data);

      if (data.status === 'completed') {
        clearInterval(pollIntervalRef.current);
        setCurrentPodcast({
          ...data.metadata,
          audio_url: data.audio_url
        });
        fetchLibrary();
        setTimeout(() => setCurrentView('player'), 1000);
      } else if (data.status === 'failed') {
        clearInterval(pollIntervalRef.current);
      }
    } catch (err) {
      console.error('Status poll error:', err);
    }
  }, []);

  // Start polling when jobId changes
  useEffect(() => {
    if (jobId && currentView === 'processing') {
      pollIntervalRef.current = setInterval(() => pollStatus(jobId), 2000);
      return () => clearInterval(pollIntervalRef.current);
    }
  }, [jobId, currentView, pollStatus]);

  // Handle file upload
  const handleUpload = async (file) => {
    setUploadedFile(file);
    setCurrentView('processing');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subject', subject);
    formData.append('chapter', chapter || file.name.replace(/\.[^/.]+$/, ''));

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setJobId(data.job_id);
    } catch (err) {
      console.error('Upload failed:', err);
      setProcessingStatus({
        status: 'failed',
        message: 'Upload failed. Please try again.',
        progress: 0
      });
    }
  };

  // Audio player controls
  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleVolumeChange = (e) => {
    const vol = parseFloat(e.target.value);
    setVolume(vol);
    if (audioRef.current) {
      audioRef.current.volume = vol;
    }
    setIsMuted(vol === 0);
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const skip = (seconds) => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, Math.min(
        audioRef.current.currentTime + seconds,
        duration
      ));
    }
  };

  const formatTime = (time) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Play a podcast from library
  const playPodcast = (podcast) => {
    setCurrentPodcast(podcast);
    setCurrentView('player');
    setIsPlaying(false);
    setCurrentTime(0);
  };

  // Delete a podcast
  const deletePodcast = async (jobId) => {
    try {
      await fetch(`${API_BASE}/podcast/${jobId}`, { method: 'DELETE' });
      fetchLibrary();
      if (currentPodcast?.job_id === jobId) {
        setCurrentPodcast(null);
        setCurrentView('home');
      }
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-spotify-black flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentView={currentView} 
        setCurrentView={setCurrentView}
        libraryCount={library.length}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-24">
        {currentView === 'home' && (
          <HomeView 
            setCurrentView={setCurrentView}
            library={library}
            playPodcast={playPodcast}
          />
        )}
        
        {currentView === 'upload' && (
          <UploadView
            subject={subject}
            setSubject={setSubject}
            chapter={chapter}
            setChapter={setChapter}
            onUpload={handleUpload}
          />
        )}
        
        {currentView === 'processing' && (
          <ProcessingView status={processingStatus} />
        )}
        
        {currentView === 'player' && currentPodcast && (
          <PlayerView podcast={currentPodcast} />
        )}
        
        {currentView === 'library' && (
          <LibraryView
            library={library}
            playPodcast={playPodcast}
            deletePodcast={deletePodcast}
          />
        )}
      </main>

      {/* Bottom Player Bar */}
      {currentPodcast && (
        <PlayerBar
          podcast={currentPodcast}
          audioRef={audioRef}
          isPlaying={isPlaying}
          togglePlay={togglePlay}
          currentTime={currentTime}
          duration={duration}
          volume={volume}
          isMuted={isMuted}
          handleSeek={handleSeek}
          handleVolumeChange={handleVolumeChange}
          toggleMute={toggleMute}
          skip={skip}
          formatTime={formatTime}
          handleTimeUpdate={handleTimeUpdate}
          handleLoadedMetadata={handleLoadedMetadata}
        />
      )}
    </div>
  );
}

// ============================================
// SIDEBAR COMPONENT
// ============================================
function Sidebar({ currentView, setCurrentView, libraryCount }) {
  const navItems = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'upload', icon: Plus, label: 'New Podcast' },
    { id: 'library', icon: Library, label: 'Your Library' },
  ];

  return (
    <aside className="w-full md:w-64 bg-black p-2 md:p-4 flex md:flex-col gap-2 border-b md:border-b-0 md:border-r border-white/5">
      {/* Logo */}
      <div className="hidden md:flex items-center gap-2 px-4 py-4 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-spotify-green to-neon-purple flex items-center justify-center">
          <Headphones className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-display font-bold text-lg leading-none">Commute</h1>
          <p className="text-xs text-spotify-green">&amp; Learn</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex md:flex-col gap-1 flex-1">
        {navItems.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setCurrentView(id)}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 flex-1 md:flex-none
              ${currentView === id 
                ? 'bg-white/10 text-white' 
                : 'text-text-secondary hover:text-white hover:bg-white/5'
              }`}
          >
            <Icon className="w-5 h-5" />
            <span className="hidden md:inline font-medium">{label}</span>
            {id === 'library' && libraryCount > 0 && (
              <span className="ml-auto text-xs bg-spotify-green text-black px-2 py-0.5 rounded-full font-semibold">
                {libraryCount}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Mobile Logo */}
      <div className="md:hidden flex items-center justify-center px-4 py-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-spotify-green to-neon-purple flex items-center justify-center">
          <Headphones className="w-4 h-4 text-white" />
        </div>
      </div>
    </aside>
  );
}

// ============================================
// HOME VIEW
// ============================================
function HomeView({ setCurrentView, library, playPodcast }) {
  return (
    <div className="p-6 md:p-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-spotify-green/20 via-spotify-dark to-neon-purple/20 p-8 md:p-12 mb-8">
        {/* Animated orbs */}
        <div className="orb orb-green w-64 h-64 -top-32 -right-32 animate-float" />
        <div className="orb orb-purple w-48 h-48 -bottom-24 -left-24 animate-float animate-delay-200" />
        
        <div className="relative z-10 max-w-2xl">
          <span className="inline-block px-3 py-1 bg-spotify-green/20 text-spotify-green text-sm font-medium rounded-full mb-4">
            🎧 India's #1 Study App
          </span>
          <h1 className="font-display text-4xl md:text-5xl font-bold mb-4 text-balance">
            Turn Notes into 
            <span className="gradient-text"> Hinglish Podcasts</span>
          </h1>
          <p className="text-text-secondary text-lg mb-6">
            Upload your JEE/NEET notes → Get AI-generated audio with Didi & Bhaiya explaining concepts. 
            Study hands-free during your commute! 🚌
          </p>
          <button 
            onClick={() => setCurrentView('upload')}
            className="btn-primary flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Create Your First Podcast
          </button>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {[
          { icon: FileText, title: 'Upload Notes', desc: 'PDF, Image, Handwritten', color: 'from-blue-500 to-cyan-500' },
          { icon: Sparkles, title: 'AI Magic', desc: 'Hinglish script generation', color: 'from-purple-500 to-pink-500' },
          { icon: Headphones, title: 'Listen Anywhere', desc: 'Offline MP3 download', color: 'from-green-500 to-emerald-500' },
        ].map(({ icon: Icon, title, desc, color }) => (
          <div key={title} className="card-elevated group hover:scale-[1.02] transition-transform">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 group-hover:shadow-lg transition-shadow`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-display font-semibold text-lg mb-1">{title}</h3>
            <p className="text-text-secondary text-sm">{desc}</p>
          </div>
        ))}
      </div>

      {/* Recent Podcasts */}
      {library.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-2xl font-bold">Recent Podcasts</h2>
            <button 
              onClick={() => setCurrentView('library')}
              className="text-text-secondary hover:text-white text-sm font-medium flex items-center gap-1"
            >
              See all <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {library.slice(0, 6).map((podcast) => (
              <PodcastCard 
                key={podcast.job_id} 
                podcast={podcast} 
                onClick={() => playPodcast(podcast)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

// ============================================
// UPLOAD VIEW
// ============================================
function UploadView({ subject, setSubject, chapter, setChapter, onUpload }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const subjects = [
    'Physics', 'Chemistry', 'Biology', 'Mathematics', 
    'English', 'Hindi', 'History', 'Geography', 'General'
  ];

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) setSelectedFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="font-display text-3xl font-bold mb-2">Create New Podcast</h1>
        <p className="text-text-secondary">Upload your notes and let AI do the magic ✨</p>
      </div>

      {/* Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`upload-zone mb-6 ${isDragging ? 'upload-zone-active' : ''} ${selectedFile ? 'border-spotify-green' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.webp"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        {selectedFile ? (
          <div className="text-center">
            <div className="w-16 h-16 rounded-xl bg-spotify-green/20 flex items-center justify-center mx-auto mb-4">
              {selectedFile.type.includes('pdf') ? (
                <FileText className="w-8 h-8 text-spotify-green" />
              ) : (
                <Image className="w-8 h-8 text-spotify-green" />
              )}
            </div>
            <p className="font-medium text-lg mb-1">{selectedFile.name}</p>
            <p className="text-text-secondary text-sm">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button 
              onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
              className="mt-4 text-red-400 hover:text-red-300 text-sm flex items-center gap-1 mx-auto"
            >
              <X className="w-4 h-4" /> Remove
            </button>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-text-secondary" />
            </div>
            <p className="font-medium text-lg mb-1">Drop your notes here</p>
            <p className="text-text-secondary text-sm">or click to browse</p>
            <p className="text-text-muted text-xs mt-4">
              Supports: PDF, JPG, PNG (Max 20MB)
            </p>
          </>
        )}
      </div>

      {/* Subject & Chapter */}
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <div>
          <label className="block text-sm font-medium mb-2">Subject</label>
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="input-field"
          >
            {subjects.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Chapter / Topic (Optional)</label>
          <input
            type="text"
            value={chapter}
            onChange={(e) => setChapter(e.target.value)}
            placeholder="e.g., Newton's Laws"
            className="input-field"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedFile}
        className={`w-full btn-primary flex items-center justify-center gap-2
          ${!selectedFile ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Sparkles className="w-5 h-5" />
        Generate Podcast
      </button>

      {/* Tips */}
      <div className="mt-8 p-4 bg-white/5 rounded-xl">
        <h4 className="font-medium mb-2 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-spotify-green" />
          Tips for best results
        </h4>
        <ul className="text-text-secondary text-sm space-y-1">
          <li>• Clear, readable handwriting works best</li>
          <li>• Include chapter headings and key formulas</li>
          <li>• Max 10 pages for focused podcasts</li>
        </ul>
      </div>
    </div>
  );
}

// ============================================
// PROCESSING VIEW
// ============================================
function ProcessingView({ status }) {
  const stages = [
    { key: 'upload', label: 'Uploading', emoji: '📤' },
    { key: 'ocr', label: 'Reading Notes', emoji: '👀' },
    { key: 'script', label: 'Writing Script', emoji: '✍️' },
    { key: 'tts', label: 'Recording Audio', emoji: '🎙️' },
    { key: 'done', label: 'Complete!', emoji: '🎉' },
  ];

  const currentStageIndex = stages.findIndex(s => s.key === status?.stage) || 0;

  return (
    <div className="p-6 md:p-8 max-w-2xl mx-auto">
      <div className="text-center mb-12">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-spotify-green to-neon-purple flex items-center justify-center mx-auto mb-6 animate-pulse-slow">
          {status?.status === 'completed' ? (
            <Check className="w-12 h-12 text-white" />
          ) : status?.status === 'failed' ? (
            <X className="w-12 h-12 text-white" />
          ) : (
            <Loader2 className="w-12 h-12 text-white animate-spin" />
          )}
        </div>
        <h1 className="font-display text-2xl font-bold mb-2">
          {status?.status === 'completed' ? 'Podcast Ready! 🎉' : 
           status?.status === 'failed' ? 'Oops! Something went wrong' :
           'Creating Your Podcast...'}
        </h1>
        <p className="text-text-secondary">{status?.message || 'Please wait...'}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-text-secondary">Progress</span>
          <span className="text-spotify-green font-medium">{status?.progress || 0}%</span>
        </div>
        <div className="progress-bar h-2">
          <div 
            className="progress-bar-fill"
            style={{ width: `${status?.progress || 0}%` }}
          />
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="space-y-3">
        {stages.map((stage, index) => (
          <div 
            key={stage.key}
            className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300
              ${index <= currentStageIndex ? 'bg-white/5' : 'opacity-40'}`}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg
              ${index < currentStageIndex ? 'bg-spotify-green text-black' :
                index === currentStageIndex ? 'bg-white/10 animate-pulse' : 'bg-white/5'}`}
            >
              {index < currentStageIndex ? <Check className="w-5 h-5" /> : stage.emoji}
            </div>
            <span className={`font-medium ${index <= currentStageIndex ? 'text-white' : 'text-text-muted'}`}>
              {stage.label}
            </span>
            {index === currentStageIndex && status?.status === 'processing' && (
              <Loader2 className="w-4 h-4 ml-auto text-spotify-green animate-spin" />
            )}
          </div>
        ))}
      </div>

      {/* Error Message */}
      {status?.status === 'failed' && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
          <p className="text-red-400 text-sm">{status.error || 'An unexpected error occurred'}</p>
        </div>
      )}
    </div>
  );
}

// ============================================
// PLAYER VIEW (Full Screen)
// ============================================
function PlayerView({ podcast }) {
  return (
    <div className="p-6 md:p-8 max-w-3xl mx-auto">
      <div className="card-elevated text-center">
        {/* Album Art */}
        <div className="w-64 h-64 rounded-2xl bg-gradient-to-br from-spotify-green via-emerald-500 to-neon-purple mx-auto mb-8 flex items-center justify-center shadow-glow-green">
          <div className="text-center">
            <Headphones className="w-16 h-16 text-white/80 mx-auto mb-2" />
            <span className="text-white/60 text-sm">{podcast.title?.split(' - ')[0] || 'Study'}</span>
          </div>
        </div>

        {/* Title & Info */}
        <h1 className="font-display text-2xl font-bold mb-2">{podcast.title}</h1>
        <p className="text-text-secondary mb-6">
          <Clock className="w-4 h-4 inline mr-1" />
          {Math.floor((podcast.duration || 0) / 60)} min podcast
        </p>

        {/* Script Preview */}
        {podcast.script && (
          <div className="text-left bg-white/5 rounded-xl p-4 mt-6">
            <h4 className="font-medium mb-3 text-spotify-green flex items-center gap-2 sticky top-0 bg-spotify-card py-2">
              <FileText className="w-4 h-4" /> Script Preview
            </h4>
            <div className="max-h-96 overflow-y-auto pr-2 script-scroll">
              <pre className="text-text-secondary text-sm whitespace-pre-wrap font-body leading-relaxed">
                {podcast.script}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================
// LIBRARY VIEW
// ============================================
function LibraryView({ library, playPodcast, deletePodcast }) {
  return (
    <div className="p-6 md:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-3xl font-bold">Your Library</h1>
        <span className="text-text-secondary">{library.length} podcasts</span>
      </div>

      {library.length === 0 ? (
        <div className="text-center py-16">
          <Music className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h3 className="text-xl font-medium mb-2">No podcasts yet</h3>
          <p className="text-text-secondary">Upload your first notes to create a podcast!</p>
        </div>
      ) : (
        <div className="space-y-2">
          {library.map((podcast) => (
            <div key={podcast.job_id} className="podcast-card group">
              <div 
                className="flex items-center gap-4 flex-1"
                onClick={() => playPodcast(podcast)}
              >
                <div className="podcast-card-art">
                  <Headphones className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">{podcast.title}</h3>
                  <p className="text-text-secondary text-sm">
                    {Math.floor((podcast.duration || 0) / 60)} min • {new Date(podcast.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Play className="w-5 h-5 text-text-muted group-hover:text-spotify-green transition-colors" />
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); deletePodcast(podcast.job_id); }}
                className="p-2 text-text-muted hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================
// PODCAST CARD COMPONENT
// ============================================
function PodcastCard({ podcast, onClick }) {
  const colors = [
    'from-red-500 to-orange-500',
    'from-green-500 to-emerald-500',
    'from-blue-500 to-cyan-500',
    'from-purple-500 to-pink-500',
    'from-yellow-500 to-amber-500',
  ];
  const colorIndex = podcast.job_id?.charCodeAt(0) % colors.length || 0;

  return (
    <div 
      onClick={onClick}
      className="card group hover:scale-[1.02] transition-transform cursor-pointer"
    >
      <div className={`w-full aspect-square rounded-lg bg-gradient-to-br ${colors[colorIndex]} flex items-center justify-center mb-4 relative overflow-hidden`}>
        <Headphones className="w-12 h-12 text-white/80" />
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-spotify-green flex items-center justify-center shadow-lg transform scale-0 group-hover:scale-100 transition-transform">
            <Play className="w-5 h-5 text-black ml-0.5" />
          </div>
        </div>
      </div>
      <h3 className="font-medium truncate">{podcast.title}</h3>
      <p className="text-text-secondary text-sm truncate">
        {Math.floor((podcast.duration || 0) / 60)} min podcast
      </p>
    </div>
  );
}

// ============================================
// BOTTOM PLAYER BAR
// ============================================
function PlayerBar({
  podcast,
  audioRef,
  isPlaying,
  togglePlay,
  currentTime,
  duration,
  volume,
  isMuted,
  handleSeek,
  handleVolumeChange,
  toggleMute,
  skip,
  formatTime,
  handleTimeUpdate,
  handleLoadedMetadata
}) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-spotify-dark/95 backdrop-blur-xl border-t border-white/5 px-4 py-3 z-50">
      <audio
        ref={audioRef}
        src={podcast.audio_url || `https://commute-learn-api.onrender.com/audio/${podcast.audio_file}`}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => {}}
      />
      
      <div className="max-w-screen-xl mx-auto flex items-center gap-4">
        {/* Song Info */}
        <div className="flex items-center gap-3 w-1/4 min-w-0">
          <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-spotify-green to-neon-purple flex-shrink-0 flex items-center justify-center">
            <Headphones className="w-6 h-6 text-white" />
          </div>
          <div className="min-w-0">
            <p className="font-medium truncate text-sm">{podcast.title}</p>
            <p className="text-text-secondary text-xs truncate">Didi & Bhaiya</p>
          </div>
        </div>

        {/* Player Controls */}
        <div className="flex-1 flex flex-col items-center gap-1">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => skip(-10)}
              className="text-text-secondary hover:text-white transition-colors"
            >
              <SkipBack className="w-5 h-5" />
            </button>
            <button
              onClick={togglePlay}
              className="w-10 h-10 rounded-full bg-white flex items-center justify-center hover:scale-105 transition-transform"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-black" />
              ) : (
                <Play className="w-5 h-5 text-black ml-0.5" />
              )}
            </button>
            <button 
              onClick={() => skip(10)}
              className="text-text-secondary hover:text-white transition-colors"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>
          
          {/* Progress */}
          <div className="w-full flex items-center gap-2 max-w-md">
            <span className="text-text-muted text-xs w-10 text-right">{formatTime(currentTime)}</span>
            <input
              type="range"
              min="0"
              max={duration || 100}
              value={currentTime}
              onChange={handleSeek}
              className="flex-1"
            />
            <span className="text-text-muted text-xs w-10">{formatTime(duration)}</span>
          </div>
        </div>

        {/* Volume & Download */}
        <div className="flex items-center gap-3 w-1/4 justify-end">
          <button onClick={toggleMute} className="text-text-secondary hover:text-white">
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 hidden md:block"
          />
          <a
            href={`https://commute-learn-api.onrender.com/api/download/${podcast.job_id}`}
            download
            className="text-text-secondary hover:text-white"
            title="Download MP3"
          >
            <Download className="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  );
}
