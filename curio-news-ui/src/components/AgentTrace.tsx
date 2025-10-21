import React, { useState, useEffect } from 'react';
import './AgentTrace.css';

interface AgentExecution {
  name: string;
  emoji: string;
  description: string;
  status: string;
  duration: string;
  startTime?: string;
  endTime?: string;
  input?: {
    prompt: string;
    contextSize: number;
  };
  output?: {
    success: boolean;
    contentLength: number;
    error?: string;
  };
  decisionDetails?: {
    [key: string]: any;
  };
  processing?: {
    model?: string;
    promptLength?: number;
    truncated?: boolean;
    temperature?: number;
    maxTokens?: number;
  };
}

interface TraceData {
  traceId: string;
  runId: string;
  status: string;
  startTime?: string;
  endTime?: string;
  totalDuration: string;
  model: string;
  region: string;
  agents: AgentExecution[];
}

interface AgentTraceProps {
  traceId: string;
  onClose: () => void;
}

const AgentTrace: React.FC<AgentTraceProps> = ({ traceId, onClose }) => {
  const [traceData, setTraceData] = useState<TraceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  useEffect(() => {
    fetchTraceData();
  }, [traceId]);

  const fetchTraceData = async () => {
    try {
      setLoading(true);
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';
      
      const response = await fetch(`${apiUrl}/trace/${traceId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTraceData(data);
      } else {
        setError(`Failed to load trace data: ${response.status}`);
      }
    } catch (err) {
      setError(`Network error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr?: string) => {
    if (!timeStr) return 'N/A';
    try {
      return new Date(timeStr).toLocaleTimeString();
    } catch {
      return timeStr;
    }
  };

  const renderDecisionDetails = (agent: AgentExecution) => {
    const details = agent.decisionDetails;
    if (!details) return null;

    return (
      <div className="decision-details">
        <h4>🧠 Decision Analysis</h4>
        {Object.entries(details).map(([key, value]) => (
          <div key={key} className="detail-item">
            <span className="detail-label">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:</span>
            <span className="detail-value">
              {Array.isArray(value) ? (
                <ul className="detail-list">
                  {value.map((item, idx) => (
                    <li key={idx}>{typeof item === 'object' ? JSON.stringify(item) : String(item)}</li>
                  ))}
                </ul>
              ) : (
                String(value)
              )}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const renderProcessingDetails = (agent: AgentExecution) => {
    const processing = agent.processing;
    if (!processing) return null;

    return (
      <div className="processing-details">
        <h4>⚙️ Processing Configuration</h4>
        <div className="processing-grid">
          {processing.model && (
            <div className="processing-item">
              <span className="processing-label">Model:</span>
              <span className="processing-value">{processing.model}</span>
            </div>
          )}
          {processing.promptLength && (
            <div className="processing-item">
              <span className="processing-label">Prompt Length:</span>
              <span className="processing-value">{processing.promptLength} chars</span>
            </div>
          )}
          {processing.temperature !== undefined && (
            <div className="processing-item">
              <span className="processing-label">Temperature:</span>
              <span className="processing-value">{processing.temperature}</span>
            </div>
          )}
          {processing.maxTokens && (
            <div className="processing-item">
              <span className="processing-label">Max Tokens:</span>
              <span className="processing-value">{processing.maxTokens}</span>
            </div>
          )}
          {processing.truncated && (
            <div className="processing-item warning">
              <span className="processing-label">⚠️ Truncated:</span>
              <span className="processing-value">Yes</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="trace-overlay">
        <div className="trace-modal">
          <div className="trace-header">
            <h2>🔍 Loading Agent Trace...</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Analyzing agent decisions...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="trace-overlay">
        <div className="trace-modal">
          <div className="trace-header">
            <h2>❌ Error Loading Trace</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="error-message">
            <p>{error}</p>
            <button onClick={fetchTraceData} className="retry-btn">🔄 Retry</button>
          </div>
        </div>
      </div>
    );
  }

  if (!traceData) {
    return null;
  }

  return (
    <div className="trace-overlay">
      <div className="trace-modal">
        <div className="trace-header">
          <div className="trace-title">
            <h2>🔍 Agent Provenance Trace</h2>
            <div className="trace-meta">
              <span className="trace-id">ID: {traceData.traceId}</span>
              <span className="trace-duration">⏱️ {traceData.totalDuration}</span>
              <span className={`trace-status ${traceData.status.toLowerCase()}`}>
                {traceData.status === 'COMPLETED' ? '✅' : '⚠️'} {traceData.status}
              </span>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="trace-content">
          {/* Overview Section */}
          <div className="trace-overview">
            <h3>📊 Execution Overview</h3>
            <div className="overview-grid">
              <div className="overview-item">
                <span className="overview-label">Model:</span>
                <span className="overview-value">{traceData.model}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">Region:</span>
                <span className="overview-value">{traceData.region}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">Start Time:</span>
                <span className="overview-value">{formatTime(traceData.startTime)}</span>
              </div>
              <div className="overview-item">
                <span className="overview-label">End Time:</span>
                <span className="overview-value">{formatTime(traceData.endTime)}</span>
              </div>
            </div>
          </div>

          {/* Agent Pipeline */}
          <div className="agent-pipeline-trace">
            <h3>🤖 Agent Execution Pipeline</h3>
            <div className="pipeline-flow">
              {traceData.agents.map((agent, index) => (
                <div 
                  key={agent.name} 
                  className={`pipeline-agent ${selectedAgent === agent.name ? 'selected' : ''} ${agent.status.toLowerCase()}`}
                  onClick={() => setSelectedAgent(selectedAgent === agent.name ? null : agent.name)}
                >
                  <div className="agent-header">
                    <span className="agent-emoji">{agent.emoji}</span>
                    <span className="agent-name">{agent.name}</span>
                    <span className="agent-duration">{agent.duration}</span>
                  </div>
                  <div className="agent-description">{agent.description}</div>
                  {index < traceData.agents.length - 1 && <div className="pipeline-arrow">→</div>}
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Agent View */}
          {selectedAgent && (
            <div className="agent-details">
              {(() => {
                const agent = traceData.agents.find(a => a.name === selectedAgent);
                if (!agent) return null;

                return (
                  <div className="agent-detail-content">
                    <div className="agent-detail-header">
                      <h3>{agent.emoji} {agent.name} - Detailed Analysis</h3>
                      <span className={`status-badge ${agent.status.toLowerCase()}`}>
                        {agent.status}
                      </span>
                    </div>

                    <div className="detail-sections">
                      {/* Input Section */}
                      <div className="detail-section">
                        <h4>📥 Input</h4>
                        <div className="input-details">
                          {agent.input?.prompt && (
                            <div className="input-item">
                              <span className="input-label">Prompt:</span>
                              <div className="input-value prompt-text">{agent.input.prompt}</div>
                            </div>
                          )}
                          {agent.input?.contextSize && (
                            <div className="input-item">
                              <span className="input-label">Context Size:</span>
                              <span className="input-value">{agent.input.contextSize} characters</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Processing Section */}
                      {renderProcessingDetails(agent)}

                      {/* Decision Details */}
                      {renderDecisionDetails(agent)}

                      {/* Output Section */}
                      <div className="detail-section">
                        <h4>📤 Output</h4>
                        <div className="output-details">
                          <div className="output-item">
                            <span className="output-label">Success:</span>
                            <span className={`output-value ${agent.output?.success ? 'success' : 'error'}`}>
                              {agent.output?.success ? '✅ Yes' : '❌ No'}
                            </span>
                          </div>
                          {agent.output?.contentLength && (
                            <div className="output-item">
                              <span className="output-label">Content Length:</span>
                              <span className="output-value">{agent.output.contentLength} characters</span>
                            </div>
                          )}
                          {agent.output?.error && (
                            <div className="output-item error">
                              <span className="output-label">Error:</span>
                              <span className="output-value">{agent.output.error}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Timing Section */}
                      <div className="detail-section">
                        <h4>⏱️ Timing</h4>
                        <div className="timing-details">
                          <div className="timing-item">
                            <span className="timing-label">Start:</span>
                            <span className="timing-value">{formatTime(agent.startTime)}</span>
                          </div>
                          <div className="timing-item">
                            <span className="timing-label">End:</span>
                            <span className="timing-value">{formatTime(agent.endTime)}</span>
                          </div>
                          <div className="timing-item">
                            <span className="timing-label">Duration:</span>
                            <span className="timing-value">{agent.duration}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        <div className="trace-footer">
          <div className="trace-info">
            <p>🔍 This trace shows the complete decision-making process of our 6 specialized Bedrock Agents.</p>
            <p>Click on any agent above to see detailed input, processing, and output information.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentTrace;