#!/usr/bin/env python3
"""
Validation script to ensure all Task 8 documentation is complete.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and has content"""
    if not os.path.exists(filepath):
        print(f"❌ Missing: {description}")
        print(f"   File: {filepath}")
        return False
    
    size = os.path.getsize(filepath)
    if size == 0:
        print(f"❌ Empty: {description}")
        print(f"   File: {filepath}")
        return False
    
    print(f"✅ Found: {description} ({size:,} bytes)")
    return True

def check_content_sections(filepath, required_sections, description):
    """Check if file contains required sections"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  {description} missing sections:")
            for section in missing_sections:
                print(f"   - {section}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    """Main validation routine"""
    print("="*60)
    print("  Task 8 Documentation Validation")
    print("="*60)
    print()
    
    base_path = ".kiro/specs/bedrock-multi-agent-architecture"
    results = []
    
    # Check main documentation files
    print("Checking Documentation Files:")
    print("-" * 60)
    
    files_to_check = [
        ("DEPLOYMENT_GUIDE.md", "Deployment Guide"),
        ("DEMO_QUICK_REFERENCE.md", "Demo Quick Reference"),
        ("TROUBLESHOOTING_FLOWCHART.md", "Troubleshooting Flowchart"),
        ("README.md", "Documentation Index"),
        ("check_agent_health.py", "Health Check Script"),
    ]
    
    for filename, description in files_to_check:
        filepath = os.path.join(base_path, filename)
        results.append(check_file_exists(filepath, description))
    
    print()
    
    # Check DEPLOYMENT_GUIDE.md sections
    print("Checking DEPLOYMENT_GUIDE.md Sections:")
    print("-" * 60)
    
    deployment_sections = [
        "Prerequisites",
        "Agent Setup",
        "Verification",
        "Troubleshooting",
        "Updating Agent Instructions",
        "Demo Presentation Guide",
        "Step-by-step guide",
        "AWS Bedrock console",
        "Common Issues",
        "Agent Collaboration Flow"
    ]
    
    deployment_path = os.path.join(base_path, "DEPLOYMENT_GUIDE.md")
    results.append(check_content_sections(
        deployment_path,
        deployment_sections,
        "DEPLOYMENT_GUIDE.md"
    ))
    
    print()
    
    # Check DEMO_QUICK_REFERENCE.md sections
    print("Checking DEMO_QUICK_REFERENCE.md Sections:")
    print("-" * 60)
    
    demo_sections = [
        "Demo Objectives",
        "5-Minute Demo Script",
        "Pre-Demo Checklist",
        "Key Talking Points",
        "Common Questions",
        "Backup Plan"
    ]
    
    demo_path = os.path.join(base_path, "DEMO_QUICK_REFERENCE.md")
    results.append(check_content_sections(
        demo_path,
        demo_sections,
        "DEMO_QUICK_REFERENCE.md"
    ))
    
    print()
    
    # Check TROUBLESHOOTING_FLOWCHART.md sections
    print("Checking TROUBLESHOOTING_FLOWCHART.md Sections:")
    print("-" * 60)
    
    troubleshooting_sections = [
        "Agent Setup Script Fails",
        "Agents Not Visible",
        "Agent Invocation Fails",
        "Malformed Response",
        "Performance Issues",
        "Diagnostic Commands",
        "Common Error Messages",
        "Health Check Script"
    ]
    
    troubleshooting_path = os.path.join(base_path, "TROUBLESHOOTING_FLOWCHART.md")
    results.append(check_content_sections(
        troubleshooting_path,
        troubleshooting_sections,
        "TROUBLESHOOTING_FLOWCHART.md"
    ))
    
    print()
    
    # Check README.md sections
    print("Checking README.md Sections:")
    print("-" * 60)
    
    readme_sections = [
        "Documentation Overview",
        "Document Guide",
        "Quick Navigation",
        "Common Workflows",
        "Getting Help",
        "Quick Start"
    ]
    
    readme_path = os.path.join(base_path, "README.md")
    results.append(check_content_sections(
        readme_path,
        readme_sections,
        "README.md"
    ))
    
    print()
    
    # Summary
    print("="*60)
    print("  Validation Summary")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(results)
    failed_checks = total_checks - passed_checks
    
    print(f"Total Checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {failed_checks}")
    print()
    
    if failed_checks == 0:
        print("🎉 All documentation validation checks passed!")
        print("Task 8 is complete and ready for review.")
        return 0
    else:
        print(f"⚠️  {failed_checks} validation check(s) failed.")
        print("Please review and fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
