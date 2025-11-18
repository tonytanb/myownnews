import React, { useState, useEffect } from 'react';
import './App.css';
import AudioPlayer from './components/AudioPlayer';
import NewsItems from './components/NewsItems';
import InteractiveTranscript from './components/InteractiveTranscript';
import AgentTrace from './components/AgentTrace';
import AgentCollaborationTrace from './components/AgentCollaborationTrace';
import WeekendRecommendations from './components/WeekendRecommendations';
import MediaGallery from './components/MediaGallery';
import DebuggingDashboard from './components/DebuggingDashboard';
import CurioCardStack from './components/cards/CurioCardStack';
import { api } from './utils/api';

interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text?: string;
  image?: string;
  relevance_score?: number;
  source?: string;
}

interface WordTiming {
  word: string;
  start: number;
  end: number;
}

const getAgentEmoji = (agentName: string): string => {
  const agentEmojis: { [key: string]: string } = {
    'NEWS_FETCHER': '📰',
    'CONTENT_CURATOR': '🎯',
    'FAVORITE_SELECTOR': '⭐',
    'SCRIPT_GENERATOR': '📝',
    'MEDIA_ENHANCER': '🎨',
    'WEEKEND_EVENTS': '🎉',
    'COMPLETED': '✅'
  };
  return agentEmojis[agentName] || '🤖';
};

const getDetailedErrorMessage = (status: number, statusText: string): string => {
  switch (status) {
    case 404:
      return 'Content service not found. The news generation service may be temporarily unavailable.';
    case 500:
      return 'Server error occurred while generating content. Our AI agents may be experiencing issues.';
    case 502:
    case 503:
      return 'Service temporarily unavailable. Please try again in a few moments.';
    case 504:
      return 'Request timeout. Content generation is taking longer than expected.';
    case 429:
      return 'Too many requests. Please wait a moment before trying again.';
    default:
      return `Failed to load content: ${status} ${statusText}. Please try refreshing the page.`;
  }
};

const App: React.FC = () => {
  // Feature flag for card UI (Subtask 11.1)
  const enableCardUI = process.env.REACT_APP_ENABLE_CARD_UI === 'true';
  
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [script, setScript] = useState<string>('');
  const [wordTimings, setWordTimings] = useState<WordTiming[]>([]);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [agentStatus, setAgentStatus] = useState<string>('Ready');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [currentAgent, setCurrentAgent] = useState<string>('');
  const [showTrace, setShowTrace] = useState<boolean>(false);
  const [traceId, setTraceId] = useState<string>('');
  const [agentOutputs, setAgentOutputs] = useState<any>(null);
  const [showDebuggingDashboard, setShowDebuggingDashboard] = useState<boolean>(false);
  const [orchestrationTrace, setOrchestrationTrace] = useState<any[]>([]);
  const [showCollaborationTrace, setShowCollaborationTrace] = useState<boolean>(false);
  const [contentLoading, setContentLoading] = useState<{ [key: string]: boolean }>({
    favoriteStory: false,
    weekendRecommendations: false,
    ...(process.env.NODE_ENV === 'development' && { mediaEnhancements: false })
  });
  const [contentErrors, setContentErrors] = useState<{ [key: string]: string }>({});
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [lastPolledTime, setLastPolledTime] = useState<number>(0);
  const [retryAttempts, setRetryAttempts] = useState<{ [key: string]: number }>({
    favoriteStory: 0,
    weekendRecommendations: 0,
    mediaEnhancements: 0,
    general: 0
  });
  const [maxRetries] = useState<number>(3);
  const [showAnalytics, setShowAnalytics] = useState<boolean>(false);
  
  // Bootstrap data for card UI (Subtask 11.2)
  const [bootstrapData, setBootstrapData] = useState<any>(null);

  // Fetch initial content
  useEffect(() => {
    fetchLatestContent();
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const fetchLatestContent = async () => {
    try {
      console.log('Fetching latest content with cache-busting...');
      const data = await api.getBootstrap();
      console.log('Bootstrap data received:', data);
      
      // Store bootstrap data for card UI (Subtask 11.2)
      setBootstrapData(data);
      
      setNewsItems(data.news_items || []);
      setScript(data.script || '');
      setWordTimings(data.word_timings || []);
      setAgentStatus(data.agentStatus || 'Ready');
      if (data.traceId) {
        setTraceId(data.traceId);
      }
      if (data.orchestration_trace) {
        setOrchestrationTrace(data.orchestration_trace);
      }
      if (data.agentOutputs) {
        setAgentOutputs(data.agentOutputs);
        // Clear loading states for sections that have content
        setContentLoading(prev => ({
          ...prev,
          favoriteStory: !data.agentOutputs.favoriteStory,
          weekendRecommendations: !data.agentOutputs.weekendRecommendations,
          mediaEnhancements: !data.agentOutputs.mediaEnhancements
        }));
      } else {
        // Set loading states for missing content
        setContentLoading({
          favoriteStory: true,
          weekendRecommendations: true,
          mediaEnhancements: true
        });
      }

      // Clear any previous errors and reset retry attempts
      setContentErrors({});
      setRetryAttempts({
        favoriteStory: 0,
        weekendRecommendations: 0,
        ...(process.env.NODE_ENV === 'development' && { mediaEnhancements: 0 }),
        general: 0
      });
      setLastPolledTime(Date.now());

      // Start polling if content is incomplete
      const hasIncompleteContent = !data.agentOutputs ||
        !data.agentOutputs.favoriteStory ||
        !data.agentOutputs.weekendRecommendations ||
        !data.agentOutputs.mediaEnhancements;

      if (hasIncompleteContent && !pollingInterval) {
        startContentPolling();
      } else if (!hasIncompleteContent && pollingInterval) {
        stopContentPolling();
      }
    } catch (error: any) {
      console.error('Failed to fetch content:', error);
      setAgentStatus('Connection error');

      const errorMessage = error.response
        ? getDetailedErrorMessage(error.response.status, error.response.statusText)
        : error.message || 'Unknown error';

      setContentErrors({
        general: `Connection error: ${errorMessage}. Please check your internet connection and try again.`
      });
    }
  };

  const handleContentUpdate = (data: any) => {
    if (data.news_items) setNewsItems(data.news_items);
    if (data.script) setScript(data.script);
    if (data.word_timings) setWordTimings(data.word_timings);
    if (data.agentStatus) setAgentStatus(data.agentStatus);
    if (data.isGenerating !== undefined) setIsGenerating(data.isGenerating);
    if (data.currentAgent) setCurrentAgent(data.currentAgent);
    if (data.traceId) setTraceId(data.traceId);
    if (data.orchestration_trace) setOrchestrationTrace(data.orchestration_trace);
    if (data.agentOutputs) {
      setAgentOutputs(data.agentOutputs);
      // Update loading states based on available content
      setContentLoading(prev => ({
        ...prev,
        favoriteStory: !data.agentOutputs.favoriteStory,
        weekendRecommendations: !data.agentOutputs.weekendRecommendations,
        mediaEnhancements: !data.agentOutputs.mediaEnhancements
      }));
    }

    // Handle generation status updates
    if (data.isGenerating) {
      setIsGenerating(true);
      if (data.currentAgent) {
        setCurrentAgent(data.currentAgent);
        // Set specific loading states based on current agent
        if (data.currentAgent === 'FAVORITE_SELECTOR') {
          setContentLoading(prev => ({ ...prev, favoriteStory: true }));
        } else if (data.currentAgent === 'WEEKEND_EVENTS') {
          setContentLoading(prev => ({ ...prev, weekendRecommendations: true }));
        } else if (data.currentAgent === 'MEDIA_ENHANCER') {
          setContentLoading(prev => ({ ...prev, mediaEnhancements: true }));
        }
      }

      // Start polling when generation begins
      if (!pollingInterval) {
        startContentPolling();
      }
    } else if (data.isGenerating === false) {
      setIsGenerating(false);
      setCurrentAgent('');

      // Stop polling when generation completes
      stopContentPolling();
    }
  };

  const startContentPolling = () => {
    if (pollingInterval) return; // Already polling

    console.log('Starting content polling...');
    const interval = setInterval(async () => {
      // Only poll if we haven't polled recently (avoid excessive requests)
      const timeSinceLastPoll = Date.now() - lastPolledTime;
      if (timeSinceLastPoll < 3000) return; // Wait at least 3 seconds between polls

      try {
        const data = await api.getBootstrap();
        setLastPolledTime(Date.now());

        // Update content if we have new data
        if (data.agentOutputs) {
          const currentOutputs = agentOutputs || {};
          const newOutputs = data.agentOutputs;

          // Check if we have new content sections
          let hasNewContent = false;
          if (!currentOutputs.favoriteStory && newOutputs.favoriteStory) {
            hasNewContent = true;
            setContentLoading(prev => ({ ...prev, favoriteStory: false }));
          }
          if (!currentOutputs.weekendRecommendations && newOutputs.weekendRecommendations) {
            hasNewContent = true;
            setContentLoading(prev => ({ ...prev, weekendRecommendations: false }));
          }
          if (!currentOutputs.mediaEnhancements && newOutputs.mediaEnhancements) {
            hasNewContent = true;
            setContentLoading(prev => ({ ...prev, mediaEnhancements: false }));
          }

          if (hasNewContent) {
            console.log('New content sections available, updating...');
            setAgentOutputs(newOutputs);
            setNewsItems(data.news_items || newsItems);
            setScript(data.script || script);
            setWordTimings(data.word_timings || wordTimings);
          }

          // Stop polling if all content is complete
          const isComplete = newOutputs.favoriteStory &&
            newOutputs.weekendRecommendations &&
            newOutputs.mediaEnhancements;

          if (isComplete) {
            console.log('All content sections complete, stopping polling');
            stopContentPolling();
          }
        } else {
          // Check if we've been polling for too long without updates
          const pollingDuration = Date.now() - lastPolledTime;
          const maxPollingTime = 5 * 60 * 1000; // 5 minutes

          if (pollingDuration > maxPollingTime) {
            console.log('Polling timeout reached, checking for failed sections');
            stopContentPolling();

            // Check which sections are still missing and mark them as potentially failed
            const currentOutputs = agentOutputs || {};
            const missingFavorite = !currentOutputs.favoriteStory;
            const missingWeekend = !currentOutputs.weekendRecommendations;
            const missingMedia = !currentOutputs.mediaEnhancements;

            if (missingFavorite || missingWeekend || missingMedia) {
              const failedSections = [];
              if (missingFavorite) failedSections.push('Favorite Story');
              if (missingWeekend) failedSections.push('Weekend Recommendations');
              if (missingMedia) failedSections.push('Visual Enhancements');

              setContentErrors(prev => ({
                ...prev,
                ...(missingFavorite && { favoriteStory: 'Content generation timed out. The Favorite Selector Agent may be experiencing issues.' }),
                ...(missingWeekend && { weekendRecommendations: 'Content generation timed out. The Weekend Events Agent may be experiencing issues.' }),
                ...(missingMedia && { mediaEnhancements: 'Content generation timed out. The Media Enhancer Agent may be experiencing issues.' })
              }));

              setContentLoading({
                favoriteStory: false,
                weekendRecommendations: false,
                mediaEnhancements: false
              });

              setAgentStatus(`Content generation incomplete. ${failedSections.join(', ')} failed to generate.`);
            }
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
        // Don't update error state during polling to avoid UI flicker
      }
    }, 5000); // Poll every 5 seconds

    setPollingInterval(interval);
  };

  const stopContentPolling = () => {
    if (pollingInterval) {
      console.log('Stopping content polling');
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  const retryContentSection = async (sectionType: 'favoriteStory' | 'weekendRecommendations' | 'mediaEnhancements') => {
    const currentAttempts = retryAttempts[sectionType];

    if (currentAttempts >= maxRetries) {
      setContentErrors(prev => ({
        ...prev,
        [sectionType]: `Maximum retry attempts (${maxRetries}) reached. Please try refreshing the page or contact support if the issue persists.`
      }));
      return;
    }

    // Increment retry count
    setRetryAttempts(prev => ({
      ...prev,
      [sectionType]: currentAttempts + 1
    }));

    // Clear previous error and set loading state
    setContentErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[sectionType];
      return newErrors;
    });

    setContentLoading(prev => ({
      ...prev,
      [sectionType]: true
    }));

    try {
      // Trigger content regeneration by calling the generate endpoint
      await api.generateFresh({
        retrySection: sectionType,
        attempt: currentAttempts + 1
      });

      // Start polling for the updated content
      if (!pollingInterval) {
        startContentPolling();
      }

      // Show success message
      setAgentStatus(`Retrying ${sectionType} generation (attempt ${currentAttempts + 1}/${maxRetries})...`);
    } catch (error: any) {
      console.error(`Failed to retry ${sectionType}:`, error);
      setContentErrors(prev => ({
        ...prev,
        [sectionType]: `Retry failed: ${error instanceof Error ? error.message : 'Unknown error'}. ${maxRetries - currentAttempts - 1} attempts remaining.`
      }));

      setContentLoading(prev => ({
        ...prev,
        [sectionType]: false
      }));
    }
  };

  const retryAllContent = async () => {
    const currentAttempts = retryAttempts.general;

    if (currentAttempts >= maxRetries) {
      setContentErrors(prev => ({
        ...prev,
        general: `Maximum retry attempts (${maxRetries}) reached. Please refresh the page or contact support if the issue persists.`
      }));
      return;
    }

    // Increment retry count
    setRetryAttempts(prev => ({
      ...prev,
      general: currentAttempts + 1
    }));

    // Clear all errors and set loading states
    setContentErrors({});
    setContentLoading({
      favoriteStory: true,
      weekendRecommendations: true,
      mediaEnhancements: true
    });

    setAgentStatus(`Retrying content generation (attempt ${currentAttempts + 1}/${maxRetries})...`);

    // Retry fetching content
    await fetchLatestContent();
  };

  // Conditional rendering based on feature flag (Subtask 11.1)
  // Requirements: 9.7
  if (enableCardUI && bootstrapData) {
    return (
      <div className="app app--card-ui">
        {/* Card UI Mode */}
        <CurioCardStack 
          bootstrapData={bootstrapData}
          audioUrl={bootstrapData.audio_url}
        />
        
        {/* Analytics overlay for card UI (Subtask 11.3) */}
        {showAnalytics && (
          <div className="analytics-overlay">
            <button
              className="analytics-overlay__close"
              onClick={() => setShowAnalytics(false)}
              aria-label="Close analytics"
            >
              ✕
            </button>
            
            {/* Agent Collaboration Trace */}
            {orchestrationTrace && orchestrationTrace.length > 0 && (
              <div className="analytics-overlay__section">
                <h3>🤖 Agent Collaboration</h3>
                <AgentCollaborationTrace
                  orchestrationTrace={orchestrationTrace}
                  isGenerating={isGenerating}
                  currentAgent={currentAgent}
                  onClose={() => {}}
                  showAsModal={false}
                />
              </div>
            )}
            
            {/* Agent Trace */}
            {traceId && (
              <div className="analytics-overlay__section">
                <h3>🔍 Detailed Trace</h3>
                <AgentTrace
                  traceId={traceId}
                  onClose={() => {}}
                />
              </div>
            )}
          </div>
        )}
        
        {/* Analytics toggle button (floating) */}
        <button
          className="analytics-toggle-btn analytics-toggle-btn--floating"
          onClick={() => setShowAnalytics(!showAnalytics)}
          title={showAnalytics ? "Hide analytics" : "Show analytics"}
          aria-label={showAnalytics ? "Hide analytics" : "Show analytics"}
        >
          {showAnalytics ? '✕' : '📊'}
        </button>
        
        {/* Debugging Dashboard Modal */}
        {showDebuggingDashboard && (
          <DebuggingDashboard
            onClose={() => setShowDebuggingDashboard(false)}
          />
        )}
      </div>
    );
  }

  // Traditional UI Mode (existing implementation)
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">CURIO</div>
        <div className="header-actions">
          <button
            className="analytics-toggle-btn"
            onClick={() => setShowAnalytics(!showAnalytics)}
            title={showAnalytics ? "Hide analytics" : "Show analytics"}
          >
            {showAnalytics ? '📊 Hide Analytics' : '📊 Show Analytics'}
          </button>
          <div className={`agent-status ${isGenerating ? 'generating' : ''} ${pollingInterval ? 'polling' : ''}`}>
            <span className="status-indicator">
              {isGenerating ? getAgentEmoji(currentAgent) : pollingInterval ? '🔄' : '🤖'}
            </span>
            <span className="status-text">
              {isGenerating
                ? `${currentAgent}: ${agentStatus}`
                : pollingInterval
                  ? 'Checking for content updates...'
                  : agentStatus}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="date-header">
          📅 {new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>

        <div className="title-section">
          <h1>Today's Brief</h1>
          <p className="subtitle">Your world in 5 minutes</p>

          {/* Global Error Banner */}
          {contentErrors.general && (
            <div className="global-error-banner">
              <div className="error-content">
                <span className="error-icon">⚠️</span>
                <div className="error-text">
                  <p className="error-message">{contentErrors.general}</p>
                  <p className="error-help">
                    {retryAttempts.general < maxRetries
                      ? `Retry attempt ${retryAttempts.general}/${maxRetries} available.`
                      : 'Please refresh the page or contact support if the issue persists.'
                    }
                  </p>
                </div>
                <div className="error-actions">
                  {retryAttempts.general < maxRetries && (
                    <button
                      className="retry-button primary"
                      onClick={retryAllContent}
                      disabled={isGenerating}
                    >
                      🔄 Retry All Content
                    </button>
                  )}
                  <button
                    className="retry-button secondary"
                    onClick={() => window.location.reload()}
                  >
                    🔄 Refresh Page
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* NEWS FIRST - Main Content */}
        <div className="news-section">
          <h3>📰 Today's Curated Stories</h3>
          <NewsItems
            items={newsItems}
            mediaEnhancements={agentOutputs?.mediaEnhancements}
            favoriteData={agentOutputs?.favoriteStory}
          />
        </div>

        {/* Audio Player & Transcript - Combined */}
        <div className="audio-transcript-section">
          <h2>🎧 Listen to Today's Brief</h2>
          <AudioPlayer
            onContentUpdate={handleContentUpdate}
            onTimeUpdate={setCurrentTime}
            showMetadata={showAnalytics}
          />
          <div className="transcript-wrapper">
            <InteractiveTranscript
              script={script}
              wordTimings={wordTimings}
              currentTime={currentTime}
            />
          </div>
        </div>

        {/* Media Gallery - Hidden in production, available in development */}
        {process.env.NODE_ENV === 'development' && (
          <MediaGallery
            mediaData={agentOutputs?.mediaEnhancements}
            isLoading={contentLoading.mediaEnhancements}
            error={contentErrors.mediaEnhancements}
            onRetry={() => retryContentSection('mediaEnhancements')}
            retryAttempt={retryAttempts.mediaEnhancements}
            maxRetries={maxRetries}
          />
        )}

        {/* Weekend Recommendations */}
        <WeekendRecommendations
          weekendData={agentOutputs?.weekendRecommendations}
          isLoading={contentLoading.weekendRecommendations}
          error={contentErrors.weekendRecommendations}
          onRetry={() => retryContentSection('weekendRecommendations')}
          retryAttempt={retryAttempts.weekendRecommendations}
          maxRetries={maxRetries}
        />

        {/* Agent Provenance - Hidden by default, shown when analytics toggle is on */}
        {showAnalytics && (
          <div className="provenance-section">
            <div className="provenance-header">
              <h3>🔍 AI Agent Provenance</h3>
              <div className="provenance-buttons">
                <button
                  className="trace-btn"
                  onClick={() => setShowCollaborationTrace(true)}
                  title="View real-time multi-agent collaboration"
                >
                  🤖 Agent Collaboration
                </button>
                {traceId && (
                  <button
                    className="trace-btn"
                    onClick={() => setShowTrace(true)}
                  >
                    🔍 View Detailed Trace
                  </button>
                )}
                <button
                  className="debug-dashboard-btn"
                  onClick={() => setShowDebuggingDashboard(true)}
                  title="Open comprehensive debugging dashboard for agent analysis"
                >
                  🛠️ Debug Dashboard
                </button>
              </div>
            </div>
            <div className="agent-pipeline">
              <div className="agent-step">
                <span className="agent-emoji">📰</span>
                <span className="agent-name">News Fetcher</span>
                <span className="agent-desc">Gathers trending stories</span>
              </div>
              <div className="agent-step">
                <span className="agent-emoji">🎯</span>
                <span className="agent-name">Content Curator</span>
                <span className="agent-desc">Selects relevant stories</span>
              </div>
              <div className="agent-step">
                <span className="agent-emoji">⭐</span>
                <span className="agent-name">Favorite Selector</span>
                <span className="agent-desc">Picks the most interesting</span>
              </div>
              <div className="agent-step">
                <span className="agent-emoji">📝</span>
                <span className="agent-name">Script Generator</span>
                <span className="agent-desc">Creates engaging narrative</span>
              </div>
              <div className="agent-step">
                <span className="agent-emoji">🎨</span>
                <span className="agent-name">Media Enhancer</span>
                <span className="agent-desc">Adds visual elements</span>
              </div>
              <div className="agent-step">
                <span className="agent-emoji">🎉</span>
                <span className="agent-name">Weekend Events</span>
                <span className="agent-desc">Suggests activities</span>
              </div>
            </div>
            <div className="provenance-info">
              <p>💡 <strong>Full Transparency:</strong> Every decision made by our AI agents is logged and traceable.</p>
              <p>🎯 <strong>Explainable AI:</strong> See exactly why each story was selected and how the script was crafted.</p>
              <p>🔍 <strong>Judge-Ready:</strong> Click "View Detailed Trace" above to explore the complete decision-making process.</p>
            </div>
          </div>
        )}
      </main>

      {/* Agent Collaboration Trace Modal */}
      {showCollaborationTrace && (
        <AgentCollaborationTrace
          orchestrationTrace={orchestrationTrace}
          isGenerating={isGenerating}
          currentAgent={currentAgent}
          onClose={() => setShowCollaborationTrace(false)}
          showAsModal={true}
        />
      )}

      {/* Agent Trace Modal */}
      {showTrace && traceId && (
        <AgentTrace
          traceId={traceId}
          onClose={() => setShowTrace(false)}
        />
      )}

      {/* Debugging Dashboard Modal */}
      {showDebuggingDashboard && (
        <DebuggingDashboard
          onClose={() => setShowDebuggingDashboard(false)}
        />
      )}
    </div>
  );
};

export default App;