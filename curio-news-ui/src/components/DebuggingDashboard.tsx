import React, { useState, useEffect } from 'react';
import './DebuggingDashboard.css';

interface AgentAnalysis {
  agent_name: string;
  analysis_period: string;
  total_executions: number;
  success_rate: number;
  average_execution_time: number;
  common_failures: Array<{
    error_category: string;
    count: number;
    percentage: number;
    recent_examples: any[];
  }>;
  performance_trends: {
    execution_time?: {
      average: number;
      trend: string;
    };
    retry_rate?: {
      average: number;
      high_retry_percentage: number;
    };
  };
  recommendations: string[];
  health_score: number;
}

interface SystemIssue {
  type: string;
  severity: string;
  description: string;
  affected_agents: string[];
  recommended_actions: string[];
}

interface TroubleshootingGuide {
  issue_type: string;
  symptoms: string[];
  root_causes: string[];
  solutions: string[];
  prevention_tips: string[];
  related_metrics: string[];
}

interface DashboardData {
  analysis_timestamp: string;
  analysis_period: string;
  overall_metrics: {
    total_executions: number;
    success_rate: number;
    failure_rate: number;
    health_score: number;
  };
  agent_analysis: { [key: string]: AgentAnalysis };
  system_issues: SystemIssue[];
  troubleshooting_guides: TroubleshootingGuide[];
  performance_visualization: any;
}

interface RealtimeData {
  timestamp: string;
  active_orchestrations: Array<{
    run_id: string;
    current_agent: string;
    status: string;
    updated_at: string;
  }>;
  recent_metrics: any;
  system_health: {
    status: string;
    memory_usage_percent: number;
    cpu_usage_percent: number;
  };
  active_alerts: Array<{
    alarm_name: string;
    description: string;
    severity: string;
    state_reason: string;
  }>;
}

interface DebuggingDashboardProps {
  onClose: () => void;
}

const DebuggingDashboard: React.FC<DebuggingDashboardProps> = ({ onClose }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null);
  const [troubleshootingGuides, setTroubleshootingGuides] = useState<{ [key: string]: TroubleshootingGuide }>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [hoursBack, setHoursBack] = useState<number>(24);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

  useEffect(() => {
    fetchDashboardData();
    fetchRealtimeData();
    fetchTroubleshootingGuides();
    
    // Set up auto-refresh
    let refreshInterval: NodeJS.Timeout;
    if (autoRefresh) {
      refreshInterval = setInterval(() => {
        fetchRealtimeData();
        if (activeTab === 'overview') {
          fetchDashboardData();
        }
      }, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [hoursBack, autoRefresh, activeTab]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';
      
      const response = await fetch(`${apiUrl}/debugging/analysis?hours_back=${hoursBack}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setDashboardData(result.data);
        } else {
          setError(result.error || 'Failed to load dashboard data');
        }
      } else {
        setError(`Failed to load dashboard data: ${response.status}`);
      }
    } catch (err) {
      setError(`Network error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtimeData = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';
      
      const response = await fetch(`${apiUrl}/debugging/realtime`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setRealtimeData(result.data);
        }
      }
    } catch (err) {
      console.warn('Failed to fetch realtime data:', err);
    }
  };

  const fetchTroubleshootingGuides = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';
      
      const response = await fetch(`${apiUrl}/debugging/troubleshooting`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data.guides) {
          setTroubleshootingGuides(result.data.guides);
        }
      }
    } catch (err) {
      console.warn('Failed to fetch troubleshooting guides:', err);
    }
  };

  const getHealthScoreColor = (score: number): string => {
    if (score >= 80) return '#4caf50'; // Green
    if (score >= 60) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return '#f44336';
      case 'WARNING': return '#ff9800';
      case 'INFO': return '#2196f3';
      default: return '#666';
    }
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const renderOverviewTab = () => {
    if (!dashboardData) return null;

    return (
      <div className="overview-tab">
        {/* Overall Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-header">
              <h3>🎯 Overall Success Rate</h3>
            </div>
            <div className="metric-value">
              {(dashboardData.overall_metrics.success_rate * 100).toFixed(1)}%
            </div>
            <div className="metric-subtitle">
              {dashboardData.overall_metrics.total_executions} total executions
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h3>💚 System Health Score</h3>
            </div>
            <div className="metric-value" style={{ color: getHealthScoreColor(dashboardData.overall_metrics.health_score) }}>
              {dashboardData.overall_metrics.health_score.toFixed(1)}
            </div>
            <div className="metric-subtitle">
              Average across all agents
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h3>⚠️ Active Issues</h3>
            </div>
            <div className="metric-value">
              {dashboardData.system_issues.length}
            </div>
            <div className="metric-subtitle">
              System-wide issues detected
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h3>🔄 Active Orchestrations</h3>
            </div>
            <div className="metric-value">
              {realtimeData?.active_orchestrations.length || 0}
            </div>
            <div className="metric-subtitle">
              Currently running
            </div>
          </div>
        </div>

        {/* System Health Status */}
        {realtimeData?.system_health && (
          <div className="system-health-card">
            <h3>🖥️ System Health</h3>
            <div className="health-indicators">
              <div className="health-indicator">
                <span className="health-label">Status:</span>
                <span className={`health-status ${realtimeData.system_health.status.toLowerCase()}`}>
                  {realtimeData.system_health.status}
                </span>
              </div>
              <div className="health-indicator">
                <span className="health-label">Memory:</span>
                <span className="health-value">
                  {realtimeData.system_health.memory_usage_percent.toFixed(1)}%
                </span>
              </div>
              <div className="health-indicator">
                <span className="health-label">CPU:</span>
                <span className="health-value">
                  {realtimeData.system_health.cpu_usage_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Active Alerts */}
        {realtimeData?.active_alerts && realtimeData.active_alerts.length > 0 && (
          <div className="alerts-section">
            <h3>🚨 Active Alerts</h3>
            <div className="alerts-list">
              {realtimeData.active_alerts.map((alert, index) => (
                <div key={index} className={`alert-item ${alert.severity.toLowerCase()}`}>
                  <div className="alert-header">
                    <span className="alert-name">{alert.alarm_name}</span>
                    <span className="alert-severity">{alert.severity}</span>
                  </div>
                  <div className="alert-description">{alert.description}</div>
                  <div className="alert-reason">{alert.state_reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Issues */}
        {dashboardData.system_issues.length > 0 && (
          <div className="system-issues-section">
            <h3>⚠️ System Issues</h3>
            <div className="issues-list">
              {dashboardData.system_issues.map((issue, index) => (
                <div key={index} className={`issue-item ${issue.severity.toLowerCase()}`}>
                  <div className="issue-header">
                    <span className="issue-type">{issue.type.replace(/_/g, ' ')}</span>
                    <span className="issue-severity">{issue.severity}</span>
                  </div>
                  <div className="issue-description">{issue.description}</div>
                  <div className="issue-affected">
                    Affected agents: {issue.affected_agents.join(', ')}
                  </div>
                  <div className="issue-actions">
                    <strong>Recommended actions:</strong>
                    <ul>
                      {issue.recommended_actions.map((action, actionIndex) => (
                        <li key={actionIndex}>{action}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAgentAnalysisTab = () => {
    if (!dashboardData) return null;

    const agents = Object.keys(dashboardData.agent_analysis);

    return (
      <div className="agent-analysis-tab">
        <div className="agent-selector">
          <button
            className={selectedAgent === null ? 'active' : ''}
            onClick={() => setSelectedAgent(null)}
          >
            All Agents
          </button>
          {agents.map(agent => (
            <button
              key={agent}
              className={selectedAgent === agent ? 'active' : ''}
              onClick={() => setSelectedAgent(agent)}
            >
              {agent.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        {selectedAgent === null ? (
          // Show all agents overview
          <div className="agents-grid">
            {agents.map(agent => {
              const analysis = dashboardData.agent_analysis[agent];
              return (
                <div key={agent} className="agent-card" onClick={() => setSelectedAgent(agent)}>
                  <div className="agent-header">
                    <h4>{agent.replace(/_/g, ' ')}</h4>
                    <div 
                      className="health-score"
                      style={{ color: getHealthScoreColor(analysis.health_score) }}
                    >
                      {analysis.health_score.toFixed(1)}
                    </div>
                  </div>
                  <div className="agent-metrics">
                    <div className="agent-metric">
                      <span className="metric-label">Success Rate:</span>
                      <span className="metric-value">{(analysis.success_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="agent-metric">
                      <span className="metric-label">Avg Time:</span>
                      <span className="metric-value">{formatDuration(analysis.average_execution_time)}</span>
                    </div>
                    <div className="agent-metric">
                      <span className="metric-label">Executions:</span>
                      <span className="metric-value">{analysis.total_executions}</span>
                    </div>
                  </div>
                  {analysis.common_failures.length > 0 && (
                    <div className="agent-issues">
                      <span className="issues-label">Top Issue:</span>
                      <span className="issues-value">
                        {analysis.common_failures[0].error_category} ({analysis.common_failures[0].percentage.toFixed(1)}%)
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          // Show detailed agent analysis
          <div className="agent-details">
            {(() => {
              const analysis = dashboardData.agent_analysis[selectedAgent];
              return (
                <div className="agent-detail-content">
                  <div className="agent-detail-header">
                    <h3>{selectedAgent.replace(/_/g, ' ')} - Detailed Analysis</h3>
                    <div 
                      className="health-score-large"
                      style={{ color: getHealthScoreColor(analysis.health_score) }}
                    >
                      Health Score: {analysis.health_score.toFixed(1)}
                    </div>
                  </div>

                  <div className="detail-sections">
                    {/* Performance Metrics */}
                    <div className="detail-section">
                      <h4>📊 Performance Metrics</h4>
                      <div className="metrics-grid-small">
                        <div className="metric-item">
                          <span className="metric-label">Total Executions:</span>
                          <span className="metric-value">{analysis.total_executions}</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-label">Success Rate:</span>
                          <span className="metric-value">{(analysis.success_rate * 100).toFixed(1)}%</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-label">Average Time:</span>
                          <span className="metric-value">{formatDuration(analysis.average_execution_time)}</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-label">Analysis Period:</span>
                          <span className="metric-value">{analysis.analysis_period}</span>
                        </div>
                      </div>
                    </div>

                    {/* Performance Trends */}
                    {analysis.performance_trends && Object.keys(analysis.performance_trends).length > 0 && (
                      <div className="detail-section">
                        <h4>📈 Performance Trends</h4>
                        <div className="trends-list">
                          {analysis.performance_trends.execution_time && (
                            <div className="trend-item">
                              <span className="trend-label">Execution Time Trend:</span>
                              <span className={`trend-value ${analysis.performance_trends.execution_time.trend}`}>
                                {analysis.performance_trends.execution_time.trend}
                              </span>
                            </div>
                          )}
                          {analysis.performance_trends.retry_rate && (
                            <div className="trend-item">
                              <span className="trend-label">High Retry Rate:</span>
                              <span className="trend-value">
                                {analysis.performance_trends.retry_rate.high_retry_percentage.toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Common Failures */}
                    {analysis.common_failures.length > 0 && (
                      <div className="detail-section">
                        <h4>❌ Common Failures</h4>
                        <div className="failures-list">
                          {analysis.common_failures.map((failure, index) => (
                            <div key={index} className="failure-item">
                              <div className="failure-header">
                                <span className="failure-category">{failure.error_category}</span>
                                <span className="failure-percentage">{failure.percentage.toFixed(1)}%</span>
                              </div>
                              <div className="failure-count">{failure.count} occurrences</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {analysis.recommendations.length > 0 && (
                      <div className="detail-section">
                        <h4>💡 Recommendations</h4>
                        <div className="recommendations-list">
                          {analysis.recommendations.map((recommendation, index) => (
                            <div key={index} className="recommendation-item">
                              {recommendation}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </div>
    );
  };

  const renderTroubleshootingTab = () => {
    const guideTypes = Object.keys(troubleshootingGuides);

    return (
      <div className="troubleshooting-tab">
        <div className="troubleshooting-header">
          <h3>🔧 Troubleshooting Guides</h3>
          <p>Comprehensive guides for diagnosing and resolving common agent issues</p>
        </div>

        <div className="guides-list">
          {guideTypes.map(guideType => {
            const guide = troubleshootingGuides[guideType];
            return (
              <div key={guideType} className="guide-card">
                <div className="guide-header">
                  <h4>{guide.issue_type.replace(/_/g, ' ')}</h4>
                </div>

                <div className="guide-section">
                  <h5>🔍 Symptoms</h5>
                  <ul>
                    {guide.symptoms.map((symptom, index) => (
                      <li key={index}>{symptom}</li>
                    ))}
                  </ul>
                </div>

                <div className="guide-section">
                  <h5>🎯 Root Causes</h5>
                  <ul>
                    {guide.root_causes.map((cause, index) => (
                      <li key={index}>{cause}</li>
                    ))}
                  </ul>
                </div>

                <div className="guide-section">
                  <h5>🛠️ Solutions</h5>
                  <ul>
                    {guide.solutions.map((solution, index) => (
                      <li key={index}>{solution}</li>
                    ))}
                  </ul>
                </div>

                <div className="guide-section">
                  <h5>🛡️ Prevention Tips</h5>
                  <ul>
                    {guide.prevention_tips.map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </div>

                <div className="guide-section">
                  <h5>📊 Related Metrics</h5>
                  <div className="metrics-tags">
                    {guide.related_metrics.map((metric, index) => (
                      <span key={index} className="metric-tag">{metric}</span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (loading && !dashboardData) {
    return (
      <div className="dashboard-overlay">
        <div className="dashboard-modal">
          <div className="dashboard-header">
            <h2>🔍 Loading Debugging Dashboard...</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Analyzing agent performance and system health...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="dashboard-overlay">
        <div className="dashboard-modal">
          <div className="dashboard-header">
            <h2>❌ Error Loading Dashboard</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="error-message">
            <p>{error}</p>
            <button onClick={fetchDashboardData} className="retry-btn">🔄 Retry</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-overlay">
      <div className="dashboard-modal">
        <div className="dashboard-header">
          <div className="dashboard-title">
            <h2>🔍 Agent Debugging Dashboard</h2>
            <div className="dashboard-controls">
              <select 
                value={hoursBack} 
                onChange={(e) => setHoursBack(Number(e.target.value))}
                className="time-selector"
              >
                <option value={1}>Last 1 hour</option>
                <option value={6}>Last 6 hours</option>
                <option value={24}>Last 24 hours</option>
                <option value={72}>Last 3 days</option>
                <option value={168}>Last 7 days</option>
              </select>
              <label className="auto-refresh-toggle">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
                Auto-refresh
              </label>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="dashboard-tabs">
          <button
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button
            className={activeTab === 'agents' ? 'active' : ''}
            onClick={() => setActiveTab('agents')}
          >
            🤖 Agent Analysis
          </button>
          <button
            className={activeTab === 'troubleshooting' ? 'active' : ''}
            onClick={() => setActiveTab('troubleshooting')}
          >
            🔧 Troubleshooting
          </button>
        </div>

        <div className="dashboard-content">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'agents' && renderAgentAnalysisTab()}
          {activeTab === 'troubleshooting' && renderTroubleshootingTab()}
        </div>

        <div className="dashboard-footer">
          <div className="dashboard-info">
            <p>🔍 Comprehensive debugging dashboard for agent orchestration analysis and troubleshooting.</p>
            {dashboardData && (
              <p>Last updated: {new Date(dashboardData.analysis_timestamp).toLocaleString()}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DebuggingDashboard;