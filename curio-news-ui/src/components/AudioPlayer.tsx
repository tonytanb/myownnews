import React from "react";

export default function AudioPlayer() {
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [meta, setMeta] = React.useState<{sources:string[]; generatedAt:string; why:string; traceId?:string} | null>(null);

  const playLatest = async () => {
    try {
      setError(null);
      setLoading(true);
      const r = await fetch(`${process.env.REACT_APP_API_URL}/latest`, { method: "GET" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const { audioUrl, sources, generatedAt, why, traceId } = await r.json();

      setMeta({ sources, generatedAt, why, traceId });
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (e:any) {
      setError(e?.message || "Failed to fetch latest brief.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="curio-audio">
      <button onClick={playLatest} disabled={loading} aria-busy={loading}>
        {loading ? "Preparing brief…" : "▶ Play Today's 90-sec Brief"}
      </button>
      <audio ref={audioRef} controls preload="none" />
      {error && <p style={{color:"crimson"}}>Error: {error}</p>}
      {meta && (
        <div className="provenance">
          <p><strong>Generated:</strong> {new Date(meta.generatedAt).toLocaleString()}</p>
          <p><strong>Why it made the brief:</strong> {meta.why}</p>
          <p><strong>Sources:</strong> {meta.sources.join(" · ")}</p>
          {meta.traceId && <a href={`${process.env.REACT_APP_API_URL}/trace/${meta.traceId}`} target="_blank" rel="noreferrer">View agent trace</a>}
        </div>
      )}
    </div>
  );
}