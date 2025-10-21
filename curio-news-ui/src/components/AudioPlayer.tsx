import React from "react";

interface AudioPlayerProps {
  onContentUpdate?: (data: any) => void;
  onTimeUpdate?: (time: number) => void;
}

export default function AudioPlayer({ onContentUpdate, onTimeUpdate }: AudioPlayerProps) {
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [meta, setMeta] = React.useState<{sources:string[]; generatedAt:string; why:string; traceId?:string} | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isPlaying, setIsPlaying] = React.useState(false);

  // Listen for transcript seek events
  React.useEffect(() => {
    const handleSeek = (event: CustomEvent) => {
      if (audioRef.current && event.detail.time >= 0) {
        audioRef.current.currentTime = event.detail.time;
      }
    };

    window.addEventListener('transcript-seek', handleSeek as EventListener);
    return () => {
      window.removeEventListener('transcript-seek', handleSeek as EventListener);
    };
  }, []);

  const playLatest = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Use environment variable with fallback
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';
      console.log('AudioPlayer using API URL:', apiUrl);
      
      // Use bootstrap endpoint for smart caching
      const r = await fetch(`${apiUrl}/bootstrap`, { 
        method: "GET",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      console.log('Bootstrap response status:', r.status);
      
      if (!r.ok) {
        const errorText = await r.text();
        console.error('Bootstrap API error:', r.status, r.statusText, errorText);
        throw new Error(`HTTP ${r.status}: ${r.statusText}`);
      }
      
      const data = await r.json();
      console.log('Bootstrap response data:', data);
      
      const { audioUrl, sources, generatedAt, why, traceId, shouldRefresh, agentStatus } = data;

      setMeta({ sources, generatedAt, why, traceId });
      
      // Update parent component with new content
      if (onContentUpdate) {
        onContentUpdate(data);
      }
      
      // Play audio immediately (cached content)
      if (audioRef.current && audioUrl) {
        audioRef.current.src = audioUrl;
        
        // Add comprehensive audio event listeners
        audioRef.current.ontimeupdate = () => {
          if (onTimeUpdate && audioRef.current) {
            onTimeUpdate(audioRef.current.currentTime);
          }
        };

        audioRef.current.onplay = () => {
          setIsPlaying(true);
          // Notify transcript that audio is playing
          const playEvent = new CustomEvent('audio-play');
          window.dispatchEvent(playEvent);
        };

        audioRef.current.onpause = () => {
          setIsPlaying(false);
          // Notify transcript that audio is paused
          const pauseEvent = new CustomEvent('audio-pause');
          window.dispatchEvent(pauseEvent);
        };

        audioRef.current.onended = () => {
          setIsPlaying(false);
          // Notify transcript that audio ended
          const endEvent = new CustomEvent('audio-end');
          window.dispatchEvent(endEvent);
        };
        
        await audioRef.current.play();
      }
      
      // If fresh content is being generated, show progress
      if (shouldRefresh && data.generationStarted) {
        setMeta(prev => prev ? { ...prev, why: `🤖 ${agentStatus}: ${why}` } : null);
        
        // Start real agent generation
        try {
          const generateR = await fetch(`${apiUrl}/generate-fresh`, { 
            method: "POST",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          });
          if (generateR.ok) {
            const generateData = await generateR.json();
            const runId = generateData.runId;
            
            // Poll for agent progress
            const pollInterval = setInterval(async () => {
              try {
                const statusR = await fetch(`${apiUrl}/agent-status?runId=${runId}`);
                if (statusR.ok) {
                  const statusData = await statusR.json();
                  const { currentAgent, status } = statusData;
                  
                  // Update UI with current agent
                  const agentEmojis: { [key: string]: string } = {
                    'NEWS_FETCHER': '📰',
                    'CONTENT_CURATOR': '🎯', 
                    'FAVORITE_SELECTOR': '⭐',
                    'SCRIPT_GENERATOR': '📝',
                    'MEDIA_ENHANCER': '🎨',
                    'WEEKEND_EVENTS': '🎉',
                    'COMPLETED': '✅'
                  };
                  
                  const emoji = agentEmojis[currentAgent] || '🤖';
                  setMeta(prev => prev ? { 
                    ...prev, 
                    why: `${emoji} ${currentAgent.replace('_', ' ')}: ${status}...` 
                  } : null);
                  
                  // Check if generation is complete
                  if (status === 'SUCCESS' || currentAgent === 'COMPLETED') {
                    // Get the fresh content
                    const freshR = await fetch(`${apiUrl}/latest`);
                    if (freshR.ok) {
                      const freshData = await freshR.json();
                      setMeta({ 
                        sources: freshData.sources, 
                        generatedAt: freshData.generatedAt, 
                        why: "✨ Fresh content generated by 6 specialized Bedrock Agents!", 
                        traceId: freshData.traceId 
                      });
                      
                      // Hot-swap audio
                      if (audioRef.current && freshData.audioUrl) {
                        audioRef.current.src = freshData.audioUrl;
                      }
                    }
                    clearInterval(pollInterval);
                  }
                }
              } catch (e) {
                console.log("Agent status polling error:", e);
              }
            }, 2000); // Poll every 2 seconds for agent progress
            
            // Clear polling after 2 minutes
            setTimeout(() => clearInterval(pollInterval), 120000);
          }
        } catch (e) {
          console.log("Generate fresh error:", e);
        }
      }
      
    } catch (e:any) {
      console.error('Fetch error:', e);
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
          {meta.traceId && <a href={`${process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod'}/trace/${meta.traceId}`} target="_blank" rel="noreferrer">View agent trace</a>}
        </div>
      )}
    </div>
  );
}