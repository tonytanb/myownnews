#!/usr/bin/env python3
"""
Deployment Validation for Consolidated Architecture
Deploys the system and validates it works within 5 minutes
"""

import subprocess
import time
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional

class DeploymentValidator:
    """Validates deployment of consolidated architecture"""
    
    def __init__(self):
        self.start_time = time.time()
        self.deployment_results = []
        self.api_url = None
        
    def log_step(self, step_name: str, success: bool, message: str = "", data: Any = None):
        """Log deployment step result"""
        elapsed = time.time() - self.start_time
        result = {
            'step': step_name,
            'success': success,
            'message': message,
            'elapsed_seconds': round(elapsed, 1),
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.deployment_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {step_name} ({elapsed:.1f}s): {message}")
        
        if data and not success:
            print(f"   Debug: {str(data)[:200]}...")

    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        try:
            print("🔍 Checking deployment prerequisites...")
            
            # Check if SAM CLI is available
            try:
                result = subprocess.run(['sam', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    self.log_step("Prerequisites", False, "SAM CLI not available")
                    return False
                
                sam_version = result.stdout.strip()
                print(f"   SAM CLI: {sam_version}")
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_step("Prerequisites", False, "SAM CLI not found or timeout")
                return False
            
            # Check if template.yaml exists
            if not os.path.exists('template.yaml'):
                self.log_step("Prerequisites", False, "template.yaml not found")
                return False
            
            # Check if consolidated API files exist
            required_files = [
                'api/main_handler.py',
                'api/content_generator.py',
                'api/audio_service.py'
            ]
            
            missing_files = [f for f in required_files if not os.path.exists(f)]
            if missing_files:
                self.log_step("Prerequisites", False, f"Missing files: {missing_files}")
                return False
            
            self.log_step("Prerequisites", True, "All prerequisites met")
            return True
            
        except Exception as e:
            self.log_step("Prerequisites", False, f"Exception: {str(e)}")
            return False

    def deploy_stack(self) -> bool:
        """Deploy the consolidated stack using SAM"""
        try:
            print("🚀 Deploying consolidated stack...")
            
            # Build the SAM application
            print("   Building SAM application...")
            build_result = subprocess.run(
                ['sam', 'build'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes for build
            )
            
            if build_result.returncode != 0:
                self.log_step("SAM Build", False, "Build failed", build_result.stderr)
                return False
            
            print("   ✅ SAM build completed")
            
            # Deploy the application
            print("   Deploying SAM application...")
            deploy_result = subprocess.run(
                ['sam', 'deploy', '--no-confirm-changeset', '--no-fail-on-empty-changeset'],
                capture_output=True,
                text=True,
                timeout=240  # 4 minutes for deploy
            )
            
            if deploy_result.returncode != 0:
                self.log_step("SAM Deploy", False, "Deploy failed", deploy_result.stderr)
                return False
            
            # Extract API URL from deploy output
            deploy_output = deploy_result.stdout
            
            # Look for API Gateway URL in output
            for line in deploy_output.split('\n'):
                if 'ApiGatewayUrl' in line and 'https://' in line:
                    # Extract URL from line like "ApiGatewayUrl = https://..."
                    parts = line.split('=')
                    if len(parts) > 1:
                        self.api_url = parts[1].strip()
                        break
            
            if not self.api_url:
                # Try to get it from SAM outputs
                try:
                    outputs_result = subprocess.run(
                        ['sam', 'list', 'stack-outputs', '--output', 'json'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if outputs_result.returncode == 0:
                        outputs_data = json.loads(outputs_result.stdout)
                        for output in outputs_data:
                            if output.get('OutputKey') == 'ApiGatewayUrl':
                                self.api_url = output.get('OutputValue')
                                break
                except:
                    pass
            
            if not self.api_url:
                self.log_step("SAM Deploy", False, "Could not extract API URL from deployment")
                return False
            
            self.log_step("SAM Deploy", True, f"Deployment successful, API URL: {self.api_url}")
            return True
            
        except subprocess.TimeoutExpired:
            self.log_step("SAM Deploy", False, "Deployment timeout (>4 minutes)")
            return False
        except Exception as e:
            self.log_step("SAM Deploy", False, f"Exception: {str(e)}")
            return False

    def run_health_checks(self) -> bool:
        """Run health checks on deployed system"""
        try:
            print("🏥 Running health checks...")
            
            if not self.api_url:
                self.log_step("Health Checks", False, "No API URL available")
                return False
            
            session = requests.Session()
            health_issues = []
            
            # Test bootstrap endpoint
            try:
                print("   Testing bootstrap endpoint...")
                response = session.get(f"{self.api_url}/bootstrap", timeout=15)
                
                if response.status_code != 200:
                    health_issues.append(f"Bootstrap HTTP {response.status_code}")
                else:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ['audioUrl', 'script', 'news_items', 'sources']
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if missing_fields:
                        health_issues.append(f"Bootstrap missing: {missing_fields}")
                    else:
                        print("   ✅ Bootstrap endpoint healthy")
                        
            except Exception as e:
                health_issues.append(f"Bootstrap error: {str(e)}")
            
            # Test latest endpoint
            try:
                print("   Testing latest endpoint...")
                response = session.get(f"{self.api_url}/latest", timeout=10)
                
                if response.status_code != 200:
                    health_issues.append(f"Latest HTTP {response.status_code}")
                else:
                    print("   ✅ Latest endpoint healthy")
                    
            except Exception as e:
                health_issues.append(f"Latest error: {str(e)}")
            
            # Test CORS
            try:
                print("   Testing CORS headers...")
                response = session.options(f"{self.api_url}/bootstrap", timeout=10)
                
                if response.status_code not in [200, 204]:
                    health_issues.append(f"CORS OPTIONS HTTP {response.status_code}")
                else:
                    headers = response.headers
                    if 'Access-Control-Allow-Origin' not in headers:
                        health_issues.append("Missing CORS headers")
                    else:
                        print("   ✅ CORS headers present")
                        
            except Exception as e:
                health_issues.append(f"CORS error: {str(e)}")
            
            if health_issues:
                self.log_step("Health Checks", False, f"Issues: {'; '.join(health_issues)}")
                return False
            else:
                self.log_step("Health Checks", True, "All health checks passed")
                return True
                
        except Exception as e:
            self.log_step("Health Checks", False, f"Exception: {str(e)}")
            return False

    def run_smoke_tests(self) -> bool:
        """Run smoke tests on all endpoints"""
        try:
            print("💨 Running smoke tests...")
            
            if not self.api_url:
                self.log_step("Smoke Tests", False, "No API URL available")
                return False
            
            session = requests.Session()
            smoke_issues = []
            
            # Test all main endpoints
            endpoints = [
                ('/bootstrap', 'GET'),
                ('/latest', 'GET'),
                ('/generate-fresh', 'POST')
            ]
            
            for endpoint, method in endpoints:
                try:
                    print(f"   Testing {method} {endpoint}...")
                    
                    if method == 'GET':
                        response = session.get(f"{self.api_url}{endpoint}", timeout=10)
                    else:
                        response = session.post(f"{self.api_url}{endpoint}", timeout=15)
                    
                    if response.status_code not in [200, 201, 202]:
                        smoke_issues.append(f"{endpoint} HTTP {response.status_code}")
                    else:
                        print(f"   ✅ {endpoint} responding")
                        
                except Exception as e:
                    smoke_issues.append(f"{endpoint} error: {str(e)[:50]}")
            
            # Test audio accessibility
            try:
                print("   Testing audio accessibility...")
                bootstrap_response = session.get(f"{self.api_url}/bootstrap", timeout=10)
                
                if bootstrap_response.status_code == 200:
                    data = bootstrap_response.json()
                    audio_url = data.get('audioUrl')
                    
                    if audio_url:
                        audio_response = session.head(audio_url, timeout=10)
                        if audio_response.status_code not in [200, 206]:
                            smoke_issues.append(f"Audio URL HTTP {audio_response.status_code}")
                        else:
                            print("   ✅ Audio URL accessible")
                    else:
                        smoke_issues.append("No audio URL in bootstrap")
                        
            except Exception as e:
                smoke_issues.append(f"Audio test error: {str(e)[:50]}")
            
            if smoke_issues:
                self.log_step("Smoke Tests", False, f"Issues: {'; '.join(smoke_issues[:3])}")  # Show first 3
                return False
            else:
                self.log_step("Smoke Tests", True, "All smoke tests passed")
                return True
                
        except Exception as e:
            self.log_step("Smoke Tests", False, f"Exception: {str(e)}")
            return False

    def validate_deployment_time(self) -> bool:
        """Validate deployment completed within 5 minutes"""
        elapsed = time.time() - self.start_time
        
        if elapsed > 300:  # 5 minutes
            self.log_step("Deployment Time", False, f"Deployment took {elapsed:.1f}s (>300s limit)")
            return False
        else:
            self.log_step("Deployment Time", True, f"Deployment completed in {elapsed:.1f}s (<300s limit)")
            return True

    def run_deployment_validation(self) -> Dict[str, Any]:
        """Run complete deployment validation"""
        print("🚀 Starting Deployment Validation for Consolidated Architecture")
        print("=" * 70)
        
        # Check prerequisites
        prereq_success = self.check_prerequisites()
        if not prereq_success:
            return self._generate_failure_summary("Prerequisites check failed")
        
        # Deploy the stack
        deploy_success = self.deploy_stack()
        if not deploy_success:
            return self._generate_failure_summary("Deployment failed")
        
        # Run health checks
        health_success = self.run_health_checks()
        
        # Run smoke tests
        smoke_success = self.run_smoke_tests()
        
        # Validate deployment time
        time_success = self.validate_deployment_time()
        
        # Calculate overall success
        overall_success = all([prereq_success, deploy_success, health_success, smoke_success, time_success])
        
        return self._generate_summary(overall_success)

    def _generate_failure_summary(self, reason: str) -> Dict[str, Any]:
        """Generate summary for early failure"""
        elapsed = time.time() - self.start_time
        
        print(f"\n❌ DEPLOYMENT VALIDATION FAILED: {reason}")
        print(f"Total time: {elapsed:.1f}s")
        
        return {
            'overall_success': False,
            'failure_reason': reason,
            'elapsed_seconds': elapsed,
            'deployment_results': self.deployment_results,
            'api_url': self.api_url
        }

    def _generate_summary(self, overall_success: bool) -> Dict[str, Any]:
        """Generate deployment validation summary"""
        elapsed = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("📊 Deployment Validation Results")
        print("=" * 70)
        print(f"Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"Total Time: {elapsed:.1f}s")
        print(f"API URL: {self.api_url or 'Not available'}")
        
        print("\n📋 Deployment Steps:")
        for result in self.deployment_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['step']} ({result['elapsed_seconds']}s): {result['message']}")
        
        if overall_success:
            print("\n🎉 DEPLOYMENT VALIDATION: SUCCESS")
            print("✅ Consolidated system deployed successfully")
            print("✅ All health checks passed")
            print("✅ All smoke tests passed")
            print(f"✅ Deployment completed within 5 minutes ({elapsed:.1f}s)")
            print(f"\n🌐 API URL: {self.api_url}")
            print("🚀 The consolidated architecture is ready for use!")
        else:
            print("\n⚠️ DEPLOYMENT VALIDATION: FAILED")
            failed_steps = [r for r in self.deployment_results if not r['success']]
            if failed_steps:
                print("Failed Steps:")
                for result in failed_steps:
                    print(f"  - {result['step']}: {result['message']}")
        
        return {
            'overall_success': overall_success,
            'elapsed_seconds': elapsed,
            'api_url': self.api_url,
            'deployment_results': self.deployment_results,
            'within_time_limit': elapsed <= 300,
            'validation_status': {
                'prerequisites': any(r['step'] == 'Prerequisites' and r['success'] for r in self.deployment_results),
                'deployment': any(r['step'] == 'SAM Deploy' and r['success'] for r in self.deployment_results),
                'health_checks': any(r['step'] == 'Health Checks' and r['success'] for r in self.deployment_results),
                'smoke_tests': any(r['step'] == 'Smoke Tests' and r['success'] for r in self.deployment_results),
                'deployment_time': any(r['step'] == 'Deployment Time' and r['success'] for r in self.deployment_results)
            }
        }

def main():
    """Main deployment validation execution"""
    validator = DeploymentValidator()
    results = validator.run_deployment_validation()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tests/deployment_validation_{timestamp}.json"
    
    try:
        os.makedirs("tests", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results file: {e}")
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    main()