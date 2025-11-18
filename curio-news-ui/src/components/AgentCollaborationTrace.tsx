import React, { useState, useEffect, useCallback } from 'react';
import './AgentCollaborationTrace.css';
import AgentFlowDiagram from './AgentFlowDiagram';
import PerformanceMonitor from './PerformanceMonitor';

interface AgentStatus {
  name: string;
  emoji: string;
  description: string;
  status: 'pending' | 'in-progress' | 'complete' | 'failed';
  executionTime?: number;
  startTime?: string;
  endTime?: string;
  output?: string;
  phase?: number;
  attribution?: string;
}

interface PhaseInfo {
  phase: string;
  agents: string[];
  execution_mode: 'parallel' | 'sequential';
  duration?: number;
  metadata?: any;
}

interface AgentCollaborationTraceProps {
  orchestrationTrace?: any[];
  isGenerating?: boolean;
  currentAgent?: string;
  onClose?: () => void;
  showAsModal?: boolean;
}

const AGENT_CONFIG: { [key: string]: { emoji: string; description: string; phase: number; attribution: string } } = {
  'content_curator': {
    emoji: '🎯',
    description: 'Curating and scoring news stories',
    phase: 1,
    attribution: 'News curation and quality scoring'
  },
  'social_impact_analyzer': {
    emoji: '💡',
    description: 'Analyzing social impact and relevance',
    phase: 1,
    attribution: 'Social impact analysis and scoring'
  },
  'story_selector': {
    emoji: '⭐',
    description: 'Selecting the most impactful story',
    phase: 2,
    attribution: 'Favorite story selection and reasoning'
  },
  'script_writer': {
    emoji: '📝',
    description: 'Creating engaging audio script',
    phase: 3,
    attribution: 'Audio script generation'
  },
  'entertainment_curator': {
    emoji: '🎉',
    description: 'Curating weekend recommendations',
    phase: 4,
    attribution: 'Weekend entertainment recommendations'
  },
  'media_enhancer': {
    emoji: '🎨',
    description: 'Enhancing visual content',
    phase: 4,
    attribution: 'Visual enhancements and accessibility'
  }
};

const AgentCollaborationTrace: React.FC<AgentCollaborationTraceProps> = ({
  orchestrationTrace = [],
  isGenerating = false,
  currentAgent = '',
  onClose,
  showAsModal = false
}) => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [phases, setPhases] = useState<PhaseInfo[]>([]);
  const [totalExecutionTime, setTotalExecutionTime] = useState<number>(0);

  const updateAgentStatuses = useCallback(() => {
    const agentStatuses: AgentStatus[] = [];
    const phaseData: PhaseInfo[] = [];
    let totalTime = 0;

    // Initialize all agents
    Object.entries(AGENT_CONFIG).forEach(([agentName, config]) => {
      agentStatuses.push({
        name: agentName,
        emoji: config.emoji,
        description: config.description,
        status: 'pending',
        phase: config.phase,
        attribution: config.attribution
      });
    });

    // Process orchestration trace
    if (orchestrationTrace && orchestrationTrace.length > 0) {
      orchestrationTrace.forEach((entry) => {
        if (entry.agent) {
          // Individual agent execution
          const agentIndex = agentStatuses.findIndex(a => a.name === entry.agent);
          if (agentIndex !== -1) {
            agentStatuses[agentIndex] = {
              ...agentStatuses[agentIndex],
              status: entry.status === 'success' ? 'complete' : entry.status === 'failed' ? 'failed' : 'in-progress',
              executionTime: entry.execution_time,
              startTime: entry.timestamp,
              output: entry.output_summary || ''
            };
          }
        } else if (entry.phase) {
          // Phase completion
          phaseData.push({
            phase: entry.phase,
            agents: entry.agents || [],
            execution_mode: entry.execution_mode || 'sequential',
            duration: entry.duration,
            metadata: entry.metadata
          });
          totalTime += entry.duration || 0;
        }
      });
    }

    // Update current agent if generating
    if (isGenerating && currentAgent) {
      const normalizedAgent = currentAgent.toLowerCase().replace(/_/g, '_');
      const agentIndex = agentStatuses.findIndex(a => a.name === normalizedAgent);
      if (agentIndex !== -1 && agentStatuses[agentIndex].status === 'pending') {
        agentStatuses[agentIndex].status = 'in-progress';
      }
    }

    setAgents(agentStatuses);
    setPhases(phaseData);
    setTotalExecutionTime(totalTime);
  }, [orchestrationTrace, isGenerating, currentAgent]);

  useEffect(() => {
    updateAgentStatuses();
  }, [updateAgentStatuses]);

  const formatTime = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    return `${seconds.toFixed(2)}s`;
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'complete':
        return '✅';
      case 'in-progress':
        return '⏳';
      case 'failed':
        return '❌';
      default:
        return '⏸️';
    }
  };

  const getPhaseAgents = (phaseNumber: number): AgentStatus[] => {
    return agents.filter(agent => agent.phase === phaseNumber);
  };

  const renderAgentCard = (agent: AgentStatus) => {
    const isCurrentAgent = isGenerating && currentAgent && 
      agent.name === currentAgent.toLowerCase().replace(/_/g, '_');
    
    return (
      <div
        key={agent.name}
        className={`agent-card ${agent.status} ${isCurrentAgent ? 'current-agent' : ''}`}
      >
        <div className="agent-card-header">
          <span className="agent-emoji">{agent.emoji}</span>
          <span className="agent-status-icon">{getStatusIcon(agent.status)}</span>
          {isCurrentAgent && <span className="current-badge">ACTIVE</span>}
        </div>
        <div className="agent-card-body">
          <h4 className="agent-name">{agent.name.replace(/_/g, ' ').toUpperCase()}</h4>
          <p className="agent-description">{agent.description}</p>
          {agent.executionTime && (
            <div className="agent-timing">
              <span className="timing-label">⏱️</span>
              <span className="timing-value">{formatTime(agent.executionTime)}</span>
            </div>
          )}
          {agent.status === 'complete' && agent.attribution && (
            <div className="agent-attribution">
              <span className="attribution-icon">✨</span>
              <span className="attribution-text">{agent.attribution}</span>
            </div>
          )}
          {agent.output && agent.status === 'complete' && (
            <div className="agent-output">
              <span className="output-icon">📤</span>
              <span className="output-text">{agent.output}</span>
            </div>
          )}
        </div>
        {agent.status === 'in-progress' && (
          <div className="agent-progress-bar">
            <div className="progress-bar-fill"></div>
          </div>
        )}
      </div>
    );
  };

  const getPhaseDataFlow = (phaseNumber: number): string => {
    switch (phaseNumber) {
      case 1:
        return 'Analyzing news sources and social impact';
      case 2:
        return 'Using Phase 1 outputs to select favorite story';
      case 3:
        return 'Using selected story to generate script';
      case 4:
        return 'Enhancing content with media and recommendations';
      default:
        return '';
    }
  };

  const renderPhase = (phaseNumber: number, phaseName: string) => {
    const phaseAgents = getPhaseAgents(phaseNumber);
    const phaseInfo = phases.find(p => p.phase.includes(`Phase ${phaseNumber}`));
    const isParallel = phaseInfo?.execution_mode === 'parallel';
    const dataFlow = getPhaseDataFlow(phaseNumber);

    if (phaseAgents.length === 0) return null;

    return (
      <div key={phaseNumber} className="collaboration-phase">
        <div className="phase-header">
          <div className="phase-title-group">
            <h3 className="phase-title">
              {phaseName}
              {isParallel && <span className="parallel-badge">⚡ Parallel</span>}
            </h3>
            {dataFlow && <p className="phase-data-flow">🔄 {dataFlow}</p>}
          </div>
          {phaseInfo?.duration && (
            <span className="phase-duration">{formatTime(phaseInfo.duration)}</span>
          )}
        </div>
        <div className={`phase-agents ${isParallel ? 'parallel' : 'sequential'}`}>
          {phaseAgents.map(agent => renderAgentCard(agent))}
        </div>
        {phaseNumber < 4 && (
          <div className="phase-connector">
            <div className="connector-line"></div>
            <div className="connector-arrow">↓</div>
            <div className="connector-label">Data passed to next phase</div>
          </div>
        )}
      </div>
    );
  };

  // Calculate current phase and completed phases for flow diagram
  const getCurrentPhase = (): number => {
    if (!isGenerating) return 0;
    const phaseAgents = {
      1: ['content_curator', 'social_impact_analyzer'],
      2: ['story_selector'],
      3: ['script_writer'],
      4: ['entertainment_curator', 'media_enhancer']
    };
    
    for (let phase = 4; phase >= 1; phase--) {
      const phaseAgentNames = phaseAgents[phase as keyof typeof phaseAgents];
      if (phaseAgentNames.some(name => 
        agents.some(a => a.name === name && a.status === 'in-progress')
      )) {
        return phase;
      }
    }
    return 1;
  };

  const getCompletedPhases = (): number[] => {
    const completed: number[] = [];
    const phaseAgents = {
      1: ['content_curator', 'social_impact_analyzer'],
      2: ['story_selector'],
      3: ['script_writer'],
      4: ['entertainment_curator', 'media_enhancer']
    };
    
    for (let phase = 1; phase <= 4; phase++) {
      const phaseAgentNames = phaseAgents[phase as keyof typeof phaseAgents];
      if (phaseAgentNames.every(name => 
        agents.some(a => a.name === name && a.status === 'complete')
      )) {
        completed.push(phase);
      }
    }
    return completed;
  };

  const content = (
    <div className="agent-collaboration-content">
      <div className="collaboration-header">
        <div className="header-info">
          <h2>🤖 Multi-Agent Collaboration</h2>
          <p className="header-subtitle">
            Watch our specialized Bedrock agents work together to create your personalized news briefing
          </p>
        </div>
        {totalExecutionTime > 0 && (
          <div className="total-time">
            <span className="time-label">Total Time:</span>
            <span className="time-value">{formatTime(totalExecutionTime)}</span>
          </div>
        )}
      </div>

      {/* Visual Flow Diagram */}
      <AgentFlowDiagram 
        currentPhase={getCurrentPhase()}
        completedPhases={getCompletedPhases()}
        showLabels={false}
        compact={false}
      />

      {/* Performance Monitor */}
      {orchestrationTrace.length > 0 && (
        <PerformanceMonitor 
          orchestrationTrace={orchestrationTrace}
          isGenerating={isGenerating}
          showDetailed={true}
          compact={false}
        />
      )}

      <div className="collaboration-pipeline">
        {renderPhase(1, '📊 Phase 1: Analysis')}
        {renderPhase(2, '⭐ Phase 2: Story Selection')}
        {renderPhase(3, '📝 Phase 3: Script Writing')}
        {renderPhase(4, '🎨 Phase 4: Enhancement')}
      </div>

      {isGenerating && (
        <div className="generation-status">
          <div className="status-indicator pulsing"></div>
          <span className="status-text">Agents are collaborating...</span>
        </div>
      )}

      {!isGenerating && agents.some(a => a.status === 'complete') && (
        <div className="completion-section">
          <div className="completion-message">
            <span className="completion-icon">🎉</span>
            <span className="completion-text">
              Multi-agent collaboration complete! {agents.filter(a => a.status === 'complete').length} agents contributed.
            </span>
          </div>
          <div className="collaboration-stats">
            <div className="stat-item">
              <span className="stat-value">{agents.filter(a => a.status === 'complete').length}</span>
              <span className="stat-label">Agents Completed</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{phases.length}</span>
              <span className="stat-label">Phases Executed</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {agents.filter(a => a.status === 'complete' && a.executionTime).length > 0
                  ? formatTime(
                      agents
                        .filter(a => a.status === 'complete' && a.executionTime)
                        .reduce((sum, a) => sum + (a.executionTime || 0), 0) /
                        agents.filter(a => a.status === 'complete' && a.executionTime).length
                    )
                  : 'N/A'}
              </span>
              <span className="stat-label">Avg Agent Time</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {agents.filter(a => a.status === 'complete').length > 0
                  ? Math.round((agents.filter(a => a.status === 'complete').length / agents.length) * 100)
                  : 0}%
              </span>
              <span className="stat-label">Success Rate</span>
            </div>
          </div>
        </div>
      )}

      <div className="collaboration-info">
        <div className="info-card">
          <span className="info-icon">🔍</span>
          <div className="info-content">
            <h4>Full Transparency</h4>
            <p>Every agent's decision is tracked and visible</p>
          </div>
        </div>
        <div className="info-card">
          <span className="info-icon">🤝</span>
          <div className="info-content">
            <h4>Agent Collaboration</h4>
            <p>Agents pass data to each other for better results</p>
          </div>
        </div>
        <div className="info-card">
          <span className="info-icon">⚡</span>
          <div className="info-content">
            <h4>Parallel Processing</h4>
            <p>Multiple agents work simultaneously for speed</p>
          </div>
        </div>
      </div>
    </div>
  );

  if (showAsModal) {
    return (
      <div className="collaboration-modal-overlay">
        <div className="collaboration-modal">
          <button className="modal-close-btn" onClick={onClose}>✕</button>
          {content}
        </div>
      </div>
    );
  }

  return <div className="agent-collaboration-trace">{content}</div>;
};

export default AgentCollaborationTrace;
