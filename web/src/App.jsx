import { useRef, useState } from "react";
import { runClipForge } from "./api";
import {motion, AnimatePresence} from "framer-motion";
import { useEffect } from "react";

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl bg-zinc-900 border border-zinc-800 p-6">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="text-2xl font-semibold mt-2">{value}</p>
    </div>
  );
}

function ClipCard({ clip, index, onClick }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.45, ease: "easeOut" }}
      whileHover={{y:-6}}
      onClick={onClick}
      className="group rounded-xl bg-zinc-900 border border-zinc-800 overflow-hidden hover:border-zinc-600 transition cursor-pointer"
    >
      <div className="relative h-40 overflow-hidden">
        <img
          src={`http://127.0.0.1:8000/${clip.thumbnail.replace("\\", "/")}`}
          alt="Clip thumbnail"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />

        {/* Play overlay */}
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
          <span className="text-3xl">▶</span>
        </div>
      </div>


      <div className="p-4 space-y-1">
        <p className="font-medium">
          Goal {index + 1}
        </p>
        <p className="text-sm text-zinc-400">
          Duration: {clip.duration}s
        </p>
      </div>
    </motion.div>
  );
}

function formatTime(seconds){
  const mins=Math.floor(seconds/60);
  const secs=Math.floor(seconds%60);
  return `${mins}:${secs.toString().padStart(2,'0')}`;
}

function Timeline({clips, onSelect}){
  if(!clips||clips.length===0) return null;

  const totalTime=Math.max(...clips.map(c=>c.end));

  return(
    <div className="relative mt-8">
      {/*Base Line*/}

      <div className="h-2 bg-zinc-800 rounded-full"/>
      {/*Markers*/}

      {clips.map((clip,idx)=>{
        const left=(clip.start/totalTime)*100;

        return(
          <div
            key={clip.clip_id}
            onClick={()=>onSelect(idx)}
            className="absolute top-1/2 -translate-y-1/2 group cursor-pointer"
            style={{left:`${left}%`}}
          >
            <div className="absolute -top-8 left-1/2 -translate-x-1/2 text-xs bg-zinc-900 text-zinc-100 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
              {formatTime(clip.start)}
            </div>
            <motion.div
              initial={{scale:0}}
              animate={{scale:1}}
              transition={{delay:idx*0.1}}
              className="w-4 h-4 bg-emerald-500 rounded-full border-2 border-zinc-950 hover:scale-150 transition"
            />
          </div>
        )
      })}
    </div>
  )
}

export default function App() {
  const inputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [meta, setMeta] = useState(null);
  const [activeClipIndex, setActiveClipIndex] = useState(null);
  const [toast, setToast] = useState(null);
  const [seekTime, setSeekTime] = useState(0);

  useEffect(()=>{
    if(activeClipIndex===null || !meta) return;

    const handleKeyDown=(e)=>{
      if(e.key==="Escape"){
        setActiveClipIndex(null);
        setSeekTime(0);
      }

      if(e.key==="ArrowRight"){
        setActiveClipIndex((prev)=>
          prev==meta.clips.length-1 ? 0 : prev+1
        );
      }

      if(e.key==="ArrowLeft"){
        setActiveClipIndex((prev)=>
          prev===0 ? meta.clips.length-1 : prev-1
        );
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return()=>window.removeEventListener("keydown", handleKeyDown);
  }, [activeClipIndex, meta]);

  useEffect(()=>{

    if(!toast) return;

    const timer=setTimeout(()=>{
      setToast(null);
    }, 6000);

    return () => clearTimeout(timer);

  }, [toast])

  const activeClip=activeClipIndex!==null && meta 
    ? meta.clips[activeClipIndex]
    : null;

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setLoading(true);

      const data = await runClipForge(file);

      const clips = data.metadata;
      const totalClips = clips.length;
      const totalGoals = clips.filter(c => c.type === "goal_story").length;

      const totalHighlightTime = clips.reduce(
        (sum, clip) => sum + clip.duration,
        0
      );

      const avgDuration =
        totalClips > 0 ? totalHighlightTime / totalClips : 0;

      setMeta({
        total_clips: totalClips,
        total_goals: totalGoals-1,
        total_highlight_time: Number(totalHighlightTime.toFixed(1)),
        average_clip_duration: Number(avgDuration.toFixed(1)),
        clips,
      });

      setToast({
        message: `${totalClips} clips generated succesfully!`
      })

    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  function Toast({ message }) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="fixed top-6 right-6 bg-emerald-600 text-white px-6 py-3 rounded-lg shadow-lg z-50"
      >
        {message}
      </motion.div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <span className="text-2xl">⚽</span>
          <h1 className="text-xl font-semibold tracking-tight">ClipForge</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-12">
        {/* Upload Section */}
        <section className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-8">
          <h2 className="text-2xl font-semibold mb-2">Upload Match</h2>
          <p className="text-zinc-400 mb-6">
            Upload gameplay footage to automatically generate goal highlights.
          </p>

          <div
            onClick={() => inputRef.current.click()}
            className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition
              ${
                loading
                  ? "border-emerald-500 text-emerald-400"
                  : "border-zinc-700 hover:border-zinc-500"
              }`}
          >
            {loading ? (
              <p className="font-medium">Processing video… ⏳</p>
            ) : (
              <p className="text-zinc-400">
                Click to upload a video file
              </p>
            )}
          </div>

          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={handleFileSelect}
          />
        </section>

        {/* Stats Section */}
        <section>
          <h2 className="text-xl font-semibold mb-4">
            Match Analytics
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Goals"
              value={meta ? meta.total_goals : "—"}
            />
            <StatCard
              label="Total Clips"
              value={meta ? meta.total_clips : "—"}
            />
            <StatCard
              label="Avg Duration"
              value={meta ? `${meta.average_clip_duration}s` : "—"}
            />
            <StatCard
              label="Total Highlight Time"
              value={meta ? `${meta.total_highlight_time}s` : "—"}
            />
          </div>
        </section>

        {/* Timeline Section */}

        {meta &&(
          <section>
            <h2 className="text-xl font-semibold mb-4">
              Match Timeline
            </h2>

            <Timeline
              clips={meta.clips}
              onSelect={(idx)=>{
                setActiveClipIndex(idx);
                setSeekTime(meta.clips[idx].start);
              }}
            />
          </section>
        )}

        {/* Clips Section */}
        <section>
          <h2 className="text-xl font-semibold mb-4">
            Highlight Clips
          </h2>

          {!meta && (
            <p className="text-zinc-400">
              Upload a match to generate clips.
            </p>
          )}

          {meta && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {meta.clips.map((clip, idx) => (
                <ClipCard
                  key={clip.clip_id}
                  clip={clip}
                  index={idx}
                  onClick={() => setActiveClipIndex(idx)}
                />
              ))}
            </div>
          )}

        </section>

      </main>

      <AnimatePresence>
        {activeClip && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
            onClick={() => setActiveClipIndex(null)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className="bg-zinc-900 rounded-xl p-4 w-full max-w-4xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold">
                  Goal Highlight
                </h3>
                <button
                  onClick={() => setActiveClipIndex(null)}
                  className="text-zinc-400 hover:text-zinc-200"
                >
                  ✕
                </button>
              </div>

              <video
                ref={(video) => {
                  if (video && seekTime !== null) {
                    video.currentTime = seekTime;
                  }
                }}

                src={`http://127.0.0.1:8000/${activeClip.path.replace("\\", "/")}`}
                controls
                autoPlay
                className="w-full rounded-lg"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {toast && <Toast message={toast.message} />}
      </AnimatePresence>
    </div>
  );
}
