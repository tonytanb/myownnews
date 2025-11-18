#!/usr/bin/env python3
"""
Performance Monitoring Script for Mobile Card UI
Continuously monitors key metrics and alerts on issues
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List

API_URL = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "api_response_time_ms": 3000,
            "error_rate_percent": 5,
            "response_size_kb": 500
        }
    
    def collect_metrics(self) -> Dict:
        """Collect current performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "api_response_time_ms": None,
            "api_status": None,
            "response_size_kb": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"{API_URL}/bootstrap", timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            metrics["api_response_time_ms"] = response_time
            metrics["api_status"] = response.status_code
            metrics["response_size_kb"] = len(response.content) / 1024
            
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def check_alerts(self, metrics: Dict) -> List[str]:
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        if metrics["api_response_time_ms"]:
            if metrics["api_response_time_ms"] > self.alert_thresholds["api_response_time_ms"]:
                alerts.append(
                    f"⚠️  HIGH RESPONSE TIME: {metrics['api_response_time_ms']:.0f}ms "
                    f"(threshold: {self.alert_thresholds['api_response_time_ms']}ms)"
                )
        
        if metrics["response_size_kb"]:
            if metrics["response_size_kb"] > self.alert_thresholds["response_size_kb"]:
                alerts.append(
                    f"⚠️  LARGE RESPONSE SIZE: {metrics['response_size_kb']:.1f}KB "
                    f"(threshold: {self.alert_thresholds['response_size_kb']}KB)"
                )
        
        if metrics["api_status"] and metrics["api_status"] != 200:
            alerts.append(f"❌ API ERROR: Status {metrics['api_status']}")
        
        if metrics["error"]:
            alerts.append(f"🔥 REQUEST FAILED: {metrics['error']}")
        
        return alerts
    
    def display_metrics(self, metrics: Dict, alerts: List[str]):
        """Display current metrics"""
        print(f"\n{'='*60}")
        print(f"📊 Performance Metrics - {metrics['timestamp']}")
        print(f"{'='*60}")
        
        if metrics["api_response_time_ms"]:
            status = "✅" if metrics["api_response_time_ms"] < self.alert_thresholds["api_response_time_ms"] else "⚠️"
            print(f"{status} API Response Time: {metrics['api_response_time_ms']:.0f}ms")
        
        if metrics["response_size_kb"]:
            status = "✅" if metrics["response_size_kb"] < self.alert_thresholds["response_size_kb"] else "⚠️"
            print(f"{status} Response Size: {metrics['response_size_kb']:.1f}KB")
        
        if metrics["api_status"]:
            status = "✅" if metrics["api_status"] == 200 else "❌"
            print(f"{status} API Status: {metrics['api_status']}")
        
        if alerts:
            print(f"\n🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print(f"\n✅ All metrics within normal range")
    
    def save_metrics(self):
        """Save metrics history to file"""
        filename = f".kiro/specs/mobile-card-ui-redesign/metrics-{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
    
    def generate_summary(self):
        """Generate summary statistics"""
        if not self.metrics_history:
            return
        
        valid_metrics = [m for m in self.metrics_history if m["api_response_time_ms"]]
        
        if not valid_metrics:
            return
        
        response_times = [m["api_response_time_ms"] for m in valid_metrics]
        
        print(f"\n{'='*60}")
        print(f"📈 Session Summary")
        print(f"{'='*60}")
        print(f"Total Requests: {len(self.metrics_history)}")
        print(f"Successful: {len(valid_metrics)}")
        print(f"Failed: {len(self.metrics_history) - len(valid_metrics)}")
        print(f"\nResponse Time Statistics:")
        print(f"  - Average: {sum(response_times) / len(response_times):.0f}ms")
        print(f"  - Min: {min(response_times):.0f}ms")
        print(f"  - Max: {max(response_times):.0f}ms")
    
    def monitor(self, duration_minutes: int = 5, interval_seconds: int = 30):
        """Monitor performance for specified duration"""
        print(f"🔍 Starting performance monitoring...")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Interval: {interval_seconds} seconds")
        print(f"Press Ctrl+C to stop early")
        
        end_time = time.time() + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                metrics = self.collect_metrics()
                alerts = self.check_alerts(metrics)
                
                self.metrics_history.append(metrics)
                self.display_metrics(metrics, alerts)
                
                remaining = int((end_time - time.time()) / 60)
                print(f"\n⏱️  Monitoring... ({remaining} minutes remaining)")
                
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoring stopped by user")
        
        self.save_metrics()
        self.generate_summary()

def main():
    print("🚀 Mobile Card UI Performance Monitor")
    print("="*60)
    
    monitor = PerformanceMonitor()
    
    # Monitor for 5 minutes with 30-second intervals
    monitor.monitor(duration_minutes=5, interval_seconds=30)
    
    print(f"\n✅ Monitoring complete")

if __name__ == "__main__":
    main()
