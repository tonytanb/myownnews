import React, { useState, useEffect } from 'react';
import './PerformanceMonitor.css';

interface AgentPerformance {
  name: string;
  executionTime: number;
  status: 'success' | 'failed' | 'in-progress';
  timestamp: string;
}

interface PerformanceMetrics {
  totalExecutionTime: number;
  agentPerformances: AgentPerformance[];
  successRate: number;
  averageAgentTime: number;
  targetTime: number;
  performanceGrade: 'excellent' | 'good' | 'needs-improvement';
}

interface PerformanceMonitorProps {
  orchestrationTrace?: any[];
  isGenerating?: boolean;
  showDetailed?: boolean;
  compact?: boolean;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  orchestrationTrace = [],
  isGenerating = false,
  showDetailed = true,
  compact = false
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    totalExecutionTime: 0,
    agentPerformances: [],
    successRate: 100,
    averageAgentTime: 0,
    targetTime: 10,
    performanceGrade: 'excellent'
  });

  useEffect(() => {
    calculateMetrics();
  }, [orchestrationTrace]);

  const calculateMetrics = () => {
    if (!orchestrationTrace || orchestrationTrace.length === 0) {
      return;
    }

    // Extract agent performances
    const agentPerformances: AgentPerformance[] = orchestrationTrace
      .filter(entry => entry.agent && entry.execution_time)
      .map(entry => ({
        name: entry.agent,
        executionTime: entry.execution_time,
        status: entry.status || 'success',
        timestamp: entry.timestamp
      }));

    // Calculate total time
    const totalExecutionTime = agentPerformances.reduce(
      (sum, agent) => sum + agent.executionTime,
      0
    );

    // Calculate success rate
    const successfulAgents = agentPerformances.filter(a => a.status === 'success').length;
    const successRate = agentPerformances.length > 0
      ? (successfulAgents / agentPerformances.length) * 100
      : 100;

    // Calculate average agent time
    const averageAgentTime = agentPerformances.length > 0
      ? totalExecutionTime / agentPerformances.length
      : 0;

    // Determine performance grade
    let performanceGrade: 'excellent' | 'good' | 'needs-improvement' = 'excellent';
    if (totalExecutionTime > 15) {
      performanceGrade = 'needs-improvement';
    } else if (totalExecutionTime > 10) {
      performanceGrade = 'good';
    }

    setMetrics({
      totalExecutionTime,
      agentPerformances,
      successRate,
      averageAgentTime,
      targetTime: 10,
      performanceGrade
    });
  };

  const formatTime = (seconds: number): string => {
    return `${seconds.toFixed(2)}s`;
  };

  const getGradeColor = (grade: string): string => {
    switch (grade) {
      case 'excellent':
        return '#48bb78';
      case 'good':
        return '#ed8936';
      case 'needs-improvement':
        return '#f56565';
      default:
        return '#718096';
    }
  };

  const getGradeEmoji = (grade: string): string => {
    switch (grade) {
      case 'excellent':
        return '🚀';
      case 'good':
        return '✅';
      case 'needs-improvement':
        return '⚠️';
      default:
        return '📊';
    }
  };

  const getPerformancePercentage = (): number => {
    if (metrics.totalExecutionTime === 0) return 0;
    return Math.min((metrics.targetTime / metrics.totalExecutionTime) * 100, 100);
  };

  if (compact) {
    return (
      <div className="performance-monitor compact">
        <div className="compact-metrics">
          <div className="compact-metric">
            <span className="metric-icon">⏱️</span>
            <span className="metric-value">{formatTime(metrics.totalExecutionTime)}</span>
          </div>
          <div className="compact-metric">
            <span className="metric-icon">✅</span>
            <span className="metric-value">{metrics.successRate.toFixed(0)}%</span>
          </div>
          <div className="compact-metric">
            <span className="metric-icon">{getGradeEmoji(metrics.performanceGrade)}</span>
            <span className="metric-value">{metrics.performanceGrade}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-monitor">
      <div className="monitor-header">
        <h3>⚡ Performance Metrics</h3>
        <div className="performance-grade" style={{ color: getGradeColor(metrics.performanceGrade) }}>
          <span className="grade-emoji">{getGradeEmoji(metrics.performanceGrade)}</span>
          <span className="grade-text">{metrics.performanceGrade.toUpperCase()}</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="key-metrics">
        <div className="metric-card primary">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <div className="metric-label">Total Time</div>
            <div className="metric-value">{formatTime(metrics.totalExecutionTime)}</div>
            <div className="metric-target">Target: {formatTime(metrics.targetTime)}</div>
          </div>
          <div className="metric-progress">
            <div 
              className="progress-bar"
              style={{ 
                width: `${getPerformancePercentage()}%`,
                background: getGradeColor(metrics.performanceGrade)
              }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🤖</div>
          <div className="metric-content">
            <div className="metric-label">Agents</div>
            <div className="metric-value">{metrics.agentPerformances.length}</div>
            <div className="metric-subtitle">Executed</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <div className="metric-label">Success Rate</div>
            <div className="metric-value">{metrics.successRate.toFixed(0)}%</div>
            <div className="metric-subtitle">
              {metrics.agentPerformances.filter(a => a.status === 'success').length}/
              {metrics.agentPerformances.length}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <div className="metric-label">Avg Time</div>
            <div className="metric-value">{formatTime(metrics.averageAgentTime)}</div>
            <div className="metric-subtitle">Per Agent</div>
          </div>
        </div>
      </div>

      {/* Detailed Agent Performance */}
      {showDetailed && metrics.agentPerformances.length > 0 && (
        <div className="agent-performance-details">
          <h4>Agent Execution Times</h4>
          <div className="performance-chart">
            {metrics.agentPerformances.map((agent, index) => (
              <div key={index} className="agent-performance-bar">
                <div className="agent-info">
                  <span className="agent-name">{agent.name.replace(/_/g, ' ')}</span>
                  <span className="agent-time">{formatTime(agent.executionTime)}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className={`bar-fill ${agent.status}`}
                    style={{ 
                      width: `${(agent.executionTime / Math.max(...metrics.agentPerformances.map(a => a.executionTime))) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Insights */}
      <div className="performance-insights">
        <h4>💡 Insights</h4>
        <div className="insights-list">
          {metrics.totalExecutionTime <= metrics.targetTime && (
            <div className="insight success">
              <span className="insight-icon">🎯</span>
              <span>Excellent! Under {metrics.targetTime}s target time</span>
            </div>
          )}
          {metrics.totalExecutionTime > metrics.targetTime && metrics.totalExecutionTime <= 15 && (
            <div className="insight warning">
              <span className="insight-icon">⚠️</span>
              <span>Good performance, but slightly over target</span>
            </div>
          )}
          {metrics.totalExecutionTime > 15 && (
            <div className="insight error">
              <span className="insight-icon">🔴</span>
              <span>Performance needs optimization</span>
            </div>
          )}
          {metrics.successRate === 100 && (
            <div className="insight success">
              <span className="insight-icon">✅</span>
              <span>Perfect success rate - all agents completed</span>
            </div>
          )}
          {metrics.successRate < 100 && (
            <div className="insight warning">
              <span className="insight-icon">⚠️</span>
              <span>Some agents failed - check error logs</span>
            </div>
          )}
          {metrics.agentPerformances.length >= 6 && (
            <div className="insight success">
              <span className="insight-icon">🤖</span>
              <span>Full multi-agent collaboration active</span>
            </div>
          )}
        </div>
      </div>

      {isGenerating && (
        <div className="monitoring-status">
          <div className="status-indicator pulsing"></div>
          <span>Monitoring in real-time...</span>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;
