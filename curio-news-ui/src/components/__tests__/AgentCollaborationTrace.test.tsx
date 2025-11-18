import React from 'react';
import { render, screen } from '@testing-library/react';
import AgentCollaborationTrace from '../AgentCollaborationTrace';

describe('AgentCollaborationTrace', () => {
  const mockOrchestrationTrace = [
    {
      agent: 'content_curator',
      status: 'success',
      execution_time: 1.2,
      timestamp: '2025-10-30T21:00:00Z',
      output_summary: '7 stories curated'
    },
    {
      agent: 'social_impact_analyzer',
      status: 'success',
      execution_time: 0.9,
      timestamp: '2025-10-30T21:00:01Z',
      output_summary: '4 high-impact stories identified'
    },
    {
      phase: 'Phase 1: Analysis',
      agents: ['content_curator', 'social_impact_analyzer'],
      execution_mode: 'parallel',
      duration: 1.5,
      metadata: {}
    }
  ];

  it('renders without crashing', () => {
    render(<AgentCollaborationTrace />);
    expect(screen.getByText(/Multi-Agent Collaboration/i)).toBeInTheDocument();
  });

  it('displays agent cards for all phases', () => {
    render(<AgentCollaborationTrace orchestrationTrace={mockOrchestrationTrace} />);
    
    // Check for phase headers (with emojis)
    expect(screen.getByText(/Phase 1: Analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Phase 2: Story Selection/i)).toBeInTheDocument();
    expect(screen.getByText(/Phase 3: Script Writing/i)).toBeInTheDocument();
    expect(screen.getByText(/Phase 4: Enhancement/i)).toBeInTheDocument();
  });

  it('shows agent status correctly', () => {
    render(<AgentCollaborationTrace orchestrationTrace={mockOrchestrationTrace} />);
    
    // Content curator should show as complete
    expect(screen.getByText(/CONTENT CURATOR/i)).toBeInTheDocument();
    expect(screen.getByText(/7 stories curated/i)).toBeInTheDocument();
  });

  it('displays execution times', () => {
    render(<AgentCollaborationTrace orchestrationTrace={mockOrchestrationTrace} />);
    
    // Should show execution time for completed agents
    expect(screen.getByText(/1.20s/i)).toBeInTheDocument();
    expect(screen.getByText(/0.90s/i)).toBeInTheDocument();
  });

  it('shows generating status when isGenerating is true', () => {
    render(
      <AgentCollaborationTrace 
        orchestrationTrace={mockOrchestrationTrace}
        isGenerating={true}
        currentAgent="script_writer"
      />
    );
    
    expect(screen.getByText(/Agents are collaborating/i)).toBeInTheDocument();
  });

  it('shows completion message when generation is done', () => {
    const completeTrace = [
      ...mockOrchestrationTrace,
      {
        agent: 'story_selector',
        status: 'success',
        execution_time: 0.7,
        timestamp: '2025-10-30T21:00:02Z',
        output_summary: 'Selected favorite story'
      }
    ];

    render(
      <AgentCollaborationTrace 
        orchestrationTrace={completeTrace}
        isGenerating={false}
      />
    );
    
    expect(screen.getByText(/Multi-agent collaboration complete/i)).toBeInTheDocument();
  });

  it('renders as modal when showAsModal is true', () => {
    const { container } = render(
      <AgentCollaborationTrace 
        orchestrationTrace={mockOrchestrationTrace}
        showAsModal={true}
        onClose={() => {}}
      />
    );
    
    expect(container.querySelector('.collaboration-modal-overlay')).toBeInTheDocument();
    expect(container.querySelector('.modal-close-btn')).toBeInTheDocument();
  });

  it('displays info cards with collaboration details', () => {
    render(<AgentCollaborationTrace orchestrationTrace={mockOrchestrationTrace} />);
    
    expect(screen.getByText(/Full Transparency/i)).toBeInTheDocument();
    expect(screen.getByText(/Agent Collaboration/i)).toBeInTheDocument();
    expect(screen.getByText(/Parallel Processing/i)).toBeInTheDocument();
  });

  it('shows parallel badge for parallel phases', () => {
    render(<AgentCollaborationTrace orchestrationTrace={mockOrchestrationTrace} />);
    
    // Phase 1 is parallel
    const phase1Section = screen.getByText(/Phase 1: Analysis/i).closest('.collaboration-phase');
    expect(phase1Section).toBeInTheDocument();
    expect(screen.getByText(/Parallel/i)).toBeInTheDocument();
  });

  it('handles empty orchestration trace gracefully', () => {
    render(<AgentCollaborationTrace orchestrationTrace={[]} />);
    
    // Should still render the component structure
    expect(screen.getByText(/Multi-Agent Collaboration/i)).toBeInTheDocument();
    
    // All agents should be in pending state
    expect(screen.getByText(/CONTENT CURATOR/i)).toBeInTheDocument();
    expect(screen.getByText(/SOCIAL IMPACT ANALYZER/i)).toBeInTheDocument();
  });
});
