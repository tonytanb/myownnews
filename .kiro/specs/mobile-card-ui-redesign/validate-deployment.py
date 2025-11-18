#!/usr/bin/env python3
"""
Deployment Validation Script for Mobile Card UI Redesign
Validates deployment, monitors performance, and checks functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
API_URL = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"
FRONTEND_URL = "https://main.d2s8yx8kbqwi0o.amplifyapp.com"

class DeploymentValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "performance_metrics": {},
            "overall_status": "PENDING"
        }
    
    def test_api_health(self) -> bool:
        """Test API endpoint health"""
        print("\n🔍 Testing API Health...")
        try:
            response = requests.get(f"{API_URL}/bootstrap", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ['news_items', 'script', 'word_timings']
                has_all_fields = all(field in data for field in required_fields)
                
                self.results["tests"].append({
                    "name": "API Health Check",
                    "status": "PASS" if has_all_fields else "FAIL",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "details": f"Status: {response.status_code}, Fields: {list(data.keys())}"
                })
                
                print(f"✅ API Health: PASS ({response.elapsed.total_seconds():.2f}s)")
                return True
            else:
                self.results["tests"].append({
                    "name": "API Health Check",
                    "status": "FAIL",
                    "details": f"Status: {response.status_code}"
                })
                print(f"❌ API Health: FAIL (Status {response.status_code})")
                return False
                
        except Exception as e:
            self.results["tests"].append({
                "name": "API Health Check",
                "status": "ERROR",
                "details": str(e)
            })
            print(f"❌ API Health: ERROR - {e}")
            return False
    
    def test_card_data_transformation(self) -> bool:
        """Test that API data can be transformed to card format"""
        print("\n🔍 Testing Card Data Transformation...")
        try:
            response = requests.get(f"{API_URL}/bootstrap", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate data structure for card transformation
                checks = {
                    "has_news_items": len(data.get('news_items', [])) > 0,
                    "has_script": bool(data.get('script')),
                    "has_word_timings": len(data.get('word_timings', [])) > 0,
                    "has_agent_outputs": bool(data.get('agentOutputs'))
                }
                
                all_passed = all(checks.values())
                
                self.results["tests"].append({
                    "name": "Card Data Transformation",
                    "status": "PASS" if all_passed else "FAIL",
                    "details": checks
                })
                
                if all_passed:
                    print(f"✅ Card Data: PASS")
                    print(f"   - News items: {len(data.get('news_items', []))}")
                    print(f"   - Script length: {len(data.get('script', ''))}")
                    print(f"   - Word timings: {len(data.get('word_timings', []))}")
                else:
                    print(f"❌ Card Data: FAIL")
                    for check, passed in checks.items():
                        print(f"   - {check}: {'✅' if passed else '❌'}")
                
                return all_passed
            else:
                return False
                
        except Exception as e:
            self.results["tests"].append({
                "name": "Card Data Transformation",
                "status": "ERROR",
                "details": str(e)
            })
            print(f"❌ Card Data: ERROR - {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics"""
        print("\n🔍 Testing Performance Metrics...")
        try:
            # Test API response time
            start_time = time.time()
            response = requests.get(f"{API_URL}/bootstrap", timeout=30)
            api_time = (time.time() - start_time) * 1000
            
            # Performance thresholds
            thresholds = {
                "api_response_time_ms": 3000,  # 3 seconds
                "api_response_size_kb": 500    # 500 KB
            }
            
            response_size = len(response.content) / 1024
            
            metrics = {
                "api_response_time_ms": api_time,
                "api_response_size_kb": response_size,
                "api_within_threshold": api_time < thresholds["api_response_time_ms"],
                "size_within_threshold": response_size < thresholds["api_response_size_kb"]
            }
            
            self.results["performance_metrics"] = metrics
            
            all_passed = metrics["api_within_threshold"] and metrics["size_within_threshold"]
            
            self.results["tests"].append({
                "name": "Performance Metrics",
                "status": "PASS" if all_passed else "WARN",
                "details": metrics
            })
            
            print(f"{'✅' if all_passed else '⚠️'} Performance Metrics:")
            print(f"   - API Response Time: {api_time:.0f}ms (threshold: {thresholds['api_response_time_ms']}ms)")
            print(f"   - Response Size: {response_size:.1f}KB (threshold: {thresholds['api_response_size_kb']}KB)")
            
            return True
            
        except Exception as e:
            self.results["tests"].append({
                "name": "Performance Metrics",
                "status": "ERROR",
                "details": str(e)
            })
            print(f"❌ Performance: ERROR - {e}")
            return False
    
    def test_card_ui_components(self) -> bool:
        """Test card UI component availability"""
        print("\n🔍 Testing Card UI Components...")
        
        # Check if card UI files exist
        import os
        
        required_files = [
            "curio-news-ui/src/components/cards/CurioCardStack.tsx",
            "curio-news-ui/src/components/cards/StoryCard.tsx",
            "curio-news-ui/src/components/cards/OverviewCard.tsx",
            "curio-news-ui/src/components/cards/BackgroundMedia.tsx",
            "curio-news-ui/src/components/cards/CategoryTag.tsx",
            "curio-news-ui/src/utils/cardTransformer.ts",
            "curio-news-ui/src/utils/scriptSegmentation.ts"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        all_exist = len(missing_files) == 0
        
        self.results["tests"].append({
            "name": "Card UI Components",
            "status": "PASS" if all_exist else "FAIL",
            "details": {
                "total_files": len(required_files),
                "missing_files": missing_files
            }
        })
        
        if all_exist:
            print(f"✅ Card UI Components: PASS ({len(required_files)} files)")
        else:
            print(f"❌ Card UI Components: FAIL")
            print(f"   Missing files: {missing_files}")
        
        return all_exist
    
    def test_feature_flag(self) -> bool:
        """Test feature flag configuration"""
        print("\n🔍 Testing Feature Flag Configuration...")
        
        import os
        
        env_file = "curio-news-ui/.env.production"
        
        try:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                flag_enabled = "REACT_APP_ENABLE_CARD_UI=true" in content
                
                self.results["tests"].append({
                    "name": "Feature Flag Configuration",
                    "status": "PASS" if flag_enabled else "FAIL",
                    "details": {
                        "file": env_file,
                        "flag_enabled": flag_enabled
                    }
                })
                
                if flag_enabled:
                    print(f"✅ Feature Flag: ENABLED")
                else:
                    print(f"❌ Feature Flag: DISABLED")
                    print(f"   Set REACT_APP_ENABLE_CARD_UI=true in {env_file}")
                
                return flag_enabled
            else:
                print(f"❌ Feature Flag: File not found ({env_file})")
                return False
                
        except Exception as e:
            print(f"❌ Feature Flag: ERROR - {e}")
            return False
    
    def generate_report(self):
        """Generate deployment validation report"""
        print("\n" + "="*60)
        print("📊 DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        
        # Calculate overall status
        test_statuses = [test["status"] for test in self.results["tests"]]
        
        if all(status == "PASS" for status in test_statuses):
            self.results["overall_status"] = "SUCCESS"
            status_emoji = "✅"
        elif any(status == "FAIL" or status == "ERROR" for status in test_statuses):
            self.results["overall_status"] = "FAILED"
            status_emoji = "❌"
        else:
            self.results["overall_status"] = "WARNING"
            status_emoji = "⚠️"
        
        print(f"\n{status_emoji} Overall Status: {self.results['overall_status']}")
        print(f"\nTimestamp: {self.results['timestamp']}")
        
        # Test summary
        print(f"\n📋 Test Summary:")
        pass_count = sum(1 for t in self.results["tests"] if t["status"] == "PASS")
        fail_count = sum(1 for t in self.results["tests"] if t["status"] == "FAIL")
        error_count = sum(1 for t in self.results["tests"] if t["status"] == "ERROR")
        warn_count = sum(1 for t in self.results["tests"] if t["status"] == "WARN")
        
        print(f"  ✅ Passed: {pass_count}")
        print(f"  ❌ Failed: {fail_count}")
        print(f"  ⚠️  Warnings: {warn_count}")
        print(f"  🔥 Errors: {error_count}")
        
        # Performance metrics
        if self.results["performance_metrics"]:
            print(f"\n⚡ Performance Metrics:")
            metrics = self.results["performance_metrics"]
            print(f"  - API Response Time: {metrics.get('api_response_time_ms', 0):.0f}ms")
            print(f"  - Response Size: {metrics.get('api_response_size_kb', 0):.1f}KB")
        
        # Save report
        report_file = f".kiro/specs/mobile-card-ui-redesign/deployment-validation-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        
        # Next steps
        print(f"\n📝 Next Steps:")
        if self.results["overall_status"] == "SUCCESS":
            print("  1. ✅ All tests passed - deployment is ready")
            print("  2. Monitor user feedback and analytics")
            print("  3. Check AWS CloudWatch for errors")
            print("  4. Validate mobile device testing")
        else:
            print("  1. ❌ Fix failing tests before deployment")
            print("  2. Review error details above")
            print("  3. Re-run validation after fixes")
        
        print("\n" + "="*60)
        
        return self.results["overall_status"] == "SUCCESS"

def main():
    print("🚀 Mobile Card UI Deployment Validation")
    print("="*60)
    
    validator = DeploymentValidator()
    
    # Run all tests
    tests = [
        validator.test_feature_flag,
        validator.test_card_ui_components,
        validator.test_api_health,
        validator.test_card_data_transformation,
        validator.test_performance_metrics
    ]
    
    for test in tests:
        test()
        time.sleep(0.5)  # Brief pause between tests
    
    # Generate report
    success = validator.generate_report()
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
