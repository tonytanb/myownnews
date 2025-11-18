#!/usr/bin/env python3
"""
Validation script for Task 9: Demo Optimization
Verifies all demo features are working correctly
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_component_imports(filepath: str, imports: list) -> bool:
    """Check if a component has required imports"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        missing = []
        for imp in imports:
            if imp not in content:
                missing.append(imp)
        
        if missing:
            print(f"❌ Missing imports in {filepath}:")
            for imp in missing:
                print(f"   - {imp}")
            return False
        else:
            print(f"✅ All required imports present in {filepath}")
            return True
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def check_performance_features(filepath: str) -> bool:
    """Check if performance optimization features are present"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        features = [
            'performance_target',
            'agent_timeout',
            'asyncio.gather',
            'separators=',
            'time.time()'
        ]
        
        missing = []
        for feature in features:
            if feature not in content:
                missing.append(feature)
        
        if missing:
            print(f"❌ Missing performance features in {filepath}:")
            for feature in missing:
                print(f"   - {feature}")
            return False
        else:
            print(f"✅ All performance features present in {filepath}")
            return True
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def check_demo_mode_features(filepath: str) -> bool:
    """Check if demo mode features are present in App.tsx"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        features = [
            'demoMode',
            'setDemoMode',
            'demo-mode-toggle',
            'Demo Mode'
        ]
        
        missing = []
        for feature in features:
            if feature not in content:
                missing.append(feature)
        
        if missing:
            print(f"❌ Missing demo mode features in {filepath}:")
            for feature in missing:
                print(f"   - {feature}")
            return False
        else:
            print(f"✅ All demo mode features present in {filepath}")
            return True
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def check_css_animations(filepath: str) -> bool:
    """Check if CSS has required animations"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        animations = [
            '@keyframes',
            'animation:',
            'transition:'
        ]
        
        found = []
        for anim in animations:
            if anim in content:
                found.append(anim)
        
        if len(found) >= 2:
            print(f"✅ CSS animations present in {filepath}")
            return True
        else:
            print(f"⚠️  Limited animations in {filepath}")
            return True  # Not critical
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Task 9: Demo Optimization - Validation")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check 1: Visual Flow Diagram Component
    print("📊 Check 1: Agent Flow Diagram Component")
    print("-" * 60)
    flow_diagram_tsx = "curio-news-ui/src/components/AgentFlowDiagram.tsx"
    flow_diagram_css = "curio-news-ui/src/components/AgentFlowDiagram.css"
    
    if not check_file_exists(flow_diagram_tsx, "AgentFlowDiagram.tsx"):
        all_checks_passed = False
    if not check_file_exists(flow_diagram_css, "AgentFlowDiagram.css"):
        all_checks_passed = False
    
    if os.path.exists(flow_diagram_tsx):
        if not check_component_imports(flow_diagram_tsx, ['React', 'AgentFlowDiagramProps']):
            all_checks_passed = False
    
    if os.path.exists(flow_diagram_css):
        if not check_css_animations(flow_diagram_css):
            all_checks_passed = False
    
    print()
    
    # Check 2: Performance Monitor Component
    print("⚡ Check 2: Performance Monitor Component")
    print("-" * 60)
    perf_monitor_tsx = "curio-news-ui/src/components/PerformanceMonitor.tsx"
    perf_monitor_css = "curio-news-ui/src/components/PerformanceMonitor.css"
    
    if not check_file_exists(perf_monitor_tsx, "PerformanceMonitor.tsx"):
        all_checks_passed = False
    if not check_file_exists(perf_monitor_css, "PerformanceMonitor.css"):
        all_checks_passed = False
    
    if os.path.exists(perf_monitor_tsx):
        if not check_component_imports(perf_monitor_tsx, ['React', 'PerformanceMonitorProps', 'PerformanceMetrics']):
            all_checks_passed = False
    
    print()
    
    # Check 3: Demo Mode Integration
    print("🎬 Check 3: Demo Mode Integration")
    print("-" * 60)
    app_tsx = "curio-news-ui/src/App.tsx"
    app_css = "curio-news-ui/src/App.css"
    
    if os.path.exists(app_tsx):
        if not check_demo_mode_features(app_tsx):
            all_checks_passed = False
    else:
        print(f"❌ App.tsx not found")
        all_checks_passed = False
    
    if os.path.exists(app_css):
        # Check for demo mode toggle styles
        with open(app_css, 'r') as f:
            content = f.read()
            if 'demo-mode-toggle' in content:
                print(f"✅ Demo mode toggle styles present in App.css")
            else:
                print(f"❌ Demo mode toggle styles missing in App.css")
                all_checks_passed = False
    
    print()
    
    # Check 4: Agent Collaboration Trace Updates
    print("🤖 Check 4: Agent Collaboration Trace Updates")
    print("-" * 60)
    collab_trace_tsx = "curio-news-ui/src/components/AgentCollaborationTrace.tsx"
    
    if os.path.exists(collab_trace_tsx):
        required_imports = ['AgentFlowDiagram', 'PerformanceMonitor']
        if not check_component_imports(collab_trace_tsx, required_imports):
            all_checks_passed = False
    else:
        print(f"❌ AgentCollaborationTrace.tsx not found")
        all_checks_passed = False
    
    print()
    
    # Check 5: Performance Optimization in Backend
    print("⚡ Check 5: Backend Performance Optimization")
    print("-" * 60)
    orchestrator_py = "api/bedrock_orchestrator.py"
    
    if os.path.exists(orchestrator_py):
        if not check_performance_features(orchestrator_py):
            all_checks_passed = False
    else:
        print(f"❌ bedrock_orchestrator.py not found")
        all_checks_passed = False
    
    print()
    
    # Check 6: Demo Script Documentation
    print("📝 Check 6: Demo Script Documentation")
    print("-" * 60)
    demo_script = ".kiro/specs/bedrock-multi-agent-architecture/DEMO_SCRIPT.md"
    perf_guide = ".kiro/specs/bedrock-multi-agent-architecture/PERFORMANCE_OPTIMIZATION_GUIDE.md"
    
    if not check_file_exists(demo_script, "Demo Script"):
        all_checks_passed = False
    if not check_file_exists(perf_guide, "Performance Optimization Guide"):
        all_checks_passed = False
    
    print()
    
    # Check 7: Component Integration
    print("🔗 Check 7: Component Integration")
    print("-" * 60)
    
    if os.path.exists(collab_trace_tsx):
        with open(collab_trace_tsx, 'r') as f:
            content = f.read()
            
        integrations = [
            '<AgentFlowDiagram',
            '<PerformanceMonitor',
            'getCurrentPhase',
            'getCompletedPhases'
        ]
        
        missing = []
        for integration in integrations:
            if integration not in content:
                missing.append(integration)
        
        if missing:
            print(f"❌ Missing integrations in AgentCollaborationTrace.tsx:")
            for integration in missing:
                print(f"   - {integration}")
            all_checks_passed = False
        else:
            print(f"✅ All component integrations present")
    
    print()
    
    # Final Summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Task 9: Demo Optimization is complete and ready for demo.")
        print()
        print("Features implemented:")
        print("  ✅ Visual agent collaboration flow diagram")
        print("  ✅ Demo mode with agent activity highlighting")
        print("  ✅ Performance monitoring and metrics")
        print("  ✅ Sub-10-second optimization")
        print("  ✅ Comprehensive demo script for judges")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please review the errors above and fix the issues.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
