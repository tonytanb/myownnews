/**
 * Performance Monitor Utility
 * Tracks card transition times, memory usage, and media load times
 * Requirements: 12.1, 12.2
 * Subtask: 13.3
 */

export interface PerformanceMetrics {
  cardTransitionTime: number; // milliseconds
  mediaLoadTime: number; // milliseconds
  memoryUsage: number; // MB
  timestamp: number;
  cardIndex: number;
  mediaType: 'video' | 'image' | 'gif';
  mediaUrl: string;
}

export interface PerformanceStats {
  averageTransitionTime: number;
  averageMediaLoadTime: number;
  peakMemoryUsage: number;
  totalTransitions: number;
  slowTransitions: number; // Transitions > 500ms
  failedMediaLoads: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private transitionStartTime: number | null = null;
  private mediaLoadStartTimes: Map<string, number> = new Map();
  private readonly MAX_METRICS = 100; // Keep last 100 metrics
  private readonly SLOW_TRANSITION_THRESHOLD = 500; // ms
  private memoryCheckInterval: NodeJS.Timeout | null = null;
  private currentMemoryUsage: number = 0;

  constructor() {
    // Start memory monitoring if Performance API is available
    if (this.isPerformanceAPIAvailable()) {
      this.startMemoryMonitoring();
    }
  }

  /**
   * Check if Performance API is available
   */
  private isPerformanceAPIAvailable(): boolean {
    return typeof performance !== 'undefined' && 
           typeof (performance as any).memory !== 'undefined';
  }

  /**
   * Start monitoring memory usage
   */
  private startMemoryMonitoring(): void {
    // Check memory every 5 seconds
    this.memoryCheckInterval = setInterval(() => {
      this.updateMemoryUsage();
    }, 5000);
  }

  /**
   * Update current memory usage
   */
  private updateMemoryUsage(): void {
    if (this.isPerformanceAPIAvailable() && (performance as any).memory) {
      const memory = (performance as any).memory;
      // Convert bytes to MB
      this.currentMemoryUsage = memory.usedJSHeapSize / (1024 * 1024);
    }
  }

  /**
   * Start tracking a card transition
   * Requirements: 12.1
   */
  startTransition(): void {
    this.transitionStartTime = performance.now();
  }

  /**
   * End tracking a card transition and record metrics
   * Requirements: 12.1
   */
  endTransition(cardIndex: number): number {
    if (this.transitionStartTime === null) {
      console.warn('PerformanceMonitor: endTransition called without startTransition');
      return 0;
    }

    const transitionTime = performance.now() - this.transitionStartTime;
    this.transitionStartTime = null;

    // Log slow transitions
    if (transitionTime > this.SLOW_TRANSITION_THRESHOLD) {
      console.warn(`PerformanceMonitor: Slow transition detected (${transitionTime.toFixed(2)}ms) for card ${cardIndex}`);
    }

    return transitionTime;
  }

  /**
   * Start tracking media load time
   * Requirements: 12.2
   */
  startMediaLoad(mediaUrl: string): void {
    this.mediaLoadStartTimes.set(mediaUrl, performance.now());
  }

  /**
   * End tracking media load time and record metrics
   * Requirements: 12.2
   */
  endMediaLoad(
    mediaUrl: string,
    mediaType: 'video' | 'image' | 'gif',
    cardIndex: number,
    transitionTime: number = 0
  ): number {
    const startTime = this.mediaLoadStartTimes.get(mediaUrl);
    
    if (startTime === undefined) {
      console.warn('PerformanceMonitor: endMediaLoad called without startMediaLoad');
      return 0;
    }

    const loadTime = performance.now() - startTime;
    this.mediaLoadStartTimes.delete(mediaUrl);

    // Update memory usage
    this.updateMemoryUsage();

    // Record metrics
    const metric: PerformanceMetrics = {
      cardTransitionTime: transitionTime,
      mediaLoadTime: loadTime,
      memoryUsage: this.currentMemoryUsage,
      timestamp: Date.now(),
      cardIndex,
      mediaType,
      mediaUrl
    };

    this.metrics.push(metric);

    // Keep only last MAX_METRICS
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics.shift();
    }

    // Log slow media loads
    if (loadTime > 1000) {
      console.warn(`PerformanceMonitor: Slow media load detected (${loadTime.toFixed(2)}ms) for ${mediaType}: ${mediaUrl}`);
    }

    return loadTime;
  }

  /**
   * Record a failed media load
   */
  recordMediaLoadFailure(mediaUrl: string, mediaType: 'video' | 'image' | 'gif'): void {
    console.error(`PerformanceMonitor: Media load failed for ${mediaType}: ${mediaUrl}`);
    
    // Clean up tracking
    this.mediaLoadStartTimes.delete(mediaUrl);
  }

  /**
   * Get current memory usage in MB
   * Requirements: 12.2
   */
  getCurrentMemoryUsage(): number {
    this.updateMemoryUsage();
    return this.currentMemoryUsage;
  }

  /**
   * Get performance statistics
   * Requirements: 12.1, 12.2
   */
  getStats(): PerformanceStats {
    if (this.metrics.length === 0) {
      return {
        averageTransitionTime: 0,
        averageMediaLoadTime: 0,
        peakMemoryUsage: 0,
        totalTransitions: 0,
        slowTransitions: 0,
        failedMediaLoads: 0
      };
    }

    const totalTransitionTime = this.metrics.reduce((sum, m) => sum + m.cardTransitionTime, 0);
    const totalMediaLoadTime = this.metrics.reduce((sum, m) => sum + m.mediaLoadTime, 0);
    const peakMemory = Math.max(...this.metrics.map(m => m.memoryUsage));
    const slowTransitions = this.metrics.filter(m => m.cardTransitionTime > this.SLOW_TRANSITION_THRESHOLD).length;

    return {
      averageTransitionTime: totalTransitionTime / this.metrics.length,
      averageMediaLoadTime: totalMediaLoadTime / this.metrics.length,
      peakMemoryUsage: peakMemory,
      totalTransitions: this.metrics.length,
      slowTransitions,
      failedMediaLoads: 0 // Would need separate tracking
    };
  }

  /**
   * Get recent metrics (last N)
   */
  getRecentMetrics(count: number = 10): PerformanceMetrics[] {
    return this.metrics.slice(-count);
  }

  /**
   * Get metrics for a specific card
   */
  getMetricsForCard(cardIndex: number): PerformanceMetrics[] {
    return this.metrics.filter(m => m.cardIndex === cardIndex);
  }

  /**
   * Get metrics by media type
   */
  getMetricsByMediaType(mediaType: 'video' | 'image' | 'gif'): PerformanceMetrics[] {
    return this.metrics.filter(m => m.mediaType === mediaType);
  }

  /**
   * Check if performance is acceptable
   */
  isPerformanceAcceptable(): boolean {
    const stats = this.getStats();
    
    // Performance is acceptable if:
    // - Average transition time < 500ms
    // - Average media load time < 1000ms
    // - Memory usage < 100MB
    // - Less than 20% slow transitions
    
    const slowTransitionRate = stats.totalTransitions > 0 
      ? stats.slowTransitions / stats.totalTransitions 
      : 0;

    return (
      stats.averageTransitionTime < 500 &&
      stats.averageMediaLoadTime < 1000 &&
      stats.peakMemoryUsage < 100 &&
      slowTransitionRate < 0.2
    );
  }

  /**
   * Get performance report as string
   */
  getPerformanceReport(): string {
    const stats = this.getStats();
    const isAcceptable = this.isPerformanceAcceptable();
    
    return `
Performance Report:
------------------
Average Transition Time: ${stats.averageTransitionTime.toFixed(2)}ms
Average Media Load Time: ${stats.averageMediaLoadTime.toFixed(2)}ms
Peak Memory Usage: ${stats.peakMemoryUsage.toFixed(2)}MB
Total Transitions: ${stats.totalTransitions}
Slow Transitions: ${stats.slowTransitions} (${((stats.slowTransitions / stats.totalTransitions) * 100).toFixed(1)}%)
Performance Status: ${isAcceptable ? '✓ ACCEPTABLE' : '✗ NEEDS IMPROVEMENT'}
    `.trim();
  }

  /**
   * Log performance report to console
   */
  logPerformanceReport(): void {
    console.log(this.getPerformanceReport());
  }

  /**
   * Export metrics as JSON
   */
  exportMetrics(): string {
    return JSON.stringify({
      metrics: this.metrics,
      stats: this.getStats(),
      timestamp: Date.now()
    }, null, 2);
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics = [];
    this.transitionStartTime = null;
    this.mediaLoadStartTimes.clear();
  }

  /**
   * Cleanup and stop monitoring
   */
  destroy(): void {
    if (this.memoryCheckInterval) {
      clearInterval(this.memoryCheckInterval);
      this.memoryCheckInterval = null;
    }
    this.clearMetrics();
  }
}

// Export singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export class for testing
export { PerformanceMonitor };
