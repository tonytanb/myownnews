import React from 'react';
import './AgentFlowDiagram.css';

interface AgentFlowDiagramProps {
  currentPhase?: number;
  completedPhases?: number[];
  showLabels?: boolean;
  compact?: boolean;
}

const AgentFlowDiagram: React.FC<AgentFlowDiagramProps> = ({
  currentPhase = 0,
  completedPhases = [],
  showLabels = true,
  compact = false
}) => {
  const isPhaseActive = (phase: number) => currentPhase === phase;
  const isPhaseComplete = (phase: number) => completedPhases.includes(phase);
  const isPhasePending = (phase: number) => !isPhaseActive(phase) && !isPhaseComplete(phase);

  const getPhaseClass = (phase: number) => {
    if (isPhaseComplete(phase)) return 'complete';
    if (isPhaseActive(phase)) return 'active';
    return 'pending';
  };

  return (
    <div className={`agent-flow-diagram ${compact ? 'compact' : ''}`}>
      {showLabels && (
        <div className="diagram-header">
          <h3>🤖 Multi-Agent Collaboration Flow</h3>
          <p>Watch how specialized agents work together in phases</p>
        </div>
      )}

      <div className="flow-container">
        {/* Phase 1: Parallel Analysis */}
        <div className={`flow-phase phase-1 ${getPhaseClass(1)}`}>
          <div className="phase-label">
            <span className="phase-number">1</span>
            <span className="phase-name">Analysis</span>
          </div>
          <div className="phase-agents parallel">
            <div className="agent-node">
              <span className="agent-icon">🎯</span>
              <span className="agent-name">Content Curator</span>
            </div>
            <div className="agent-node">
              <span className="agent-icon">💡</span>
              <span className="agent-name">Social Impact</span>
            </div>
          </div>
          <div className="parallel-indicator">⚡ Parallel</div>
        </div>

        {/* Connector 1 to 2 */}
        <div className={`flow-connector ${getPhaseClass(2)}`}>
          <div className="connector-line"></div>
          <div className="connector-arrow">↓</div>
          <div className="data-flow-label">Curated stories + Impact scores</div>
        </div>

        {/* Phase 2: Story Selection */}
        <div className={`flow-phase phase-2 ${getPhaseClass(2)}`}>
          <div className="phase-label">
            <span className="phase-number">2</span>
            <span className="phase-name">Selection</span>
          </div>
          <div className="phase-agents sequential">
            <div className="agent-node">
              <span className="agent-icon">⭐</span>
              <span className="agent-name">Story Selector</span>
            </div>
          </div>
        </div>

        {/* Connector 2 to 3 */}
        <div className={`flow-connector ${getPhaseClass(3)}`}>
          <div className="connector-line"></div>
          <div className="connector-arrow">↓</div>
          <div className="data-flow-label">Favorite story selected</div>
        </div>

        {/* Phase 3: Enhancement */}
        <div className={`flow-phase phase-3 ${getPhaseClass(3)}`}>
          <div className="phase-label">
            <span className="phase-number">3</span>
            <span className="phase-name">Enhancement</span>
          </div>
          <div className="phase-agents parallel">
            <div className="agent-node">
              <span className="agent-icon">🎉</span>
              <span className="agent-name">Entertainment</span>
            </div>
            <div className="agent-node">
              <span className="agent-icon">🎨</span>
              <span className="agent-name">Media Enhancer</span>
            </div>
          </div>
          <div className="parallel-indicator">⚡ Parallel</div>
        </div>

        {/* Final Output */}
        {completedPhases.includes(3) && (
          <div className="flow-output">
            <div className="output-icon">🎉</div>
            <div className="output-label">Complete News Briefing</div>
          </div>
        )}
      </div>

      {showLabels && (
        <div className="diagram-legend">
          <div className="legend-item">
            <span className="legend-dot complete"></span>
            <span>Complete</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot active"></span>
            <span>In Progress</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot pending"></span>
            <span>Pending</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentFlowDiagram;
