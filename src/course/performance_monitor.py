"""Performance Monitoring for Course Generation.

This module provides performance monitoring and timing utilities to ensure
course generation meets speed requirements:
- Course outline generation <5s
- Lesson generation <2s
- Exercise generation <3s
- MkDocs export <10s
"""

import time
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric for a single operation."""
    operation: str
    duration_seconds: float
    timestamp: datetime
    success: bool
    metadata: Dict = field(default_factory=dict)


class PerformanceMonitor:
    """Monitors and tracks performance of course generation operations.
    
    Implements Requirements 11.1, 11.2, 11.3, 11.4:
    - Tracks course outline generation time (<5s target)
    - Tracks lesson generation time (<2s target)
    - Tracks exercise generation time (<3s target)
    - Tracks MkDocs export time (<10s target)
    """
    
    # Performance targets (in seconds)
    TARGETS = {
        "course_outline": 5.0,
        "lesson_generation": 2.0,
        "exercise_generation": 3.0,
        "mkdocs_export": 10.0,
        "lesson_content": 2.0,
        "course_structure": 5.0
    }
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics: List[PerformanceMetric] = []
        self.current_operation: Optional[str] = None
        self.operation_start: Optional[float] = None
    
    @contextmanager
    def measure(self, operation: str, **metadata):
        """Context manager to measure operation duration.
        
        Args:
            operation: Name of the operation being measured
            **metadata: Additional metadata to store with the metric
            
        Yields:
            None
            
        Example:
            with monitor.measure("course_outline", file_count=100):
                generate_course_outline()
        """
        start_time = time.time()
        success = True
        
        try:
            logger.debug(f"Starting operation: {operation}")
            yield
        except Exception as e:
            success = False
            logger.error(f"Operation failed: {operation} - {e}")
            raise
        finally:
            duration = time.time() - start_time
            
            metric = PerformanceMetric(
                operation=operation,
                duration_seconds=duration,
                timestamp=datetime.now(),
                success=success,
                metadata=metadata
            )
            
            self.metrics.append(metric)
            
            # Check against target
            target = self.TARGETS.get(operation)
            if target and duration > target:
                logger.warning(
                    f"Performance target exceeded for {operation}: "
                    f"{duration:.2f}s > {target:.2f}s target"
                )
            else:
                logger.info(
                    f"Operation completed: {operation} in {duration:.2f}s"
                )
    
    def get_metrics(self, operation: Optional[str] = None) -> List[PerformanceMetric]:
        """Get performance metrics.
        
        Args:
            operation: Optional operation name to filter by
            
        Returns:
            List of performance metrics
        """
        if operation:
            return [m for m in self.metrics if m.operation == operation]
        return self.metrics
    
    def get_average_duration(self, operation: str) -> float:
        """Get average duration for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Average duration in seconds, or 0.0 if no metrics
        """
        metrics = self.get_metrics(operation)
        if not metrics:
            return 0.0
        
        return sum(m.duration_seconds for m in metrics) / len(metrics)
    
    def get_stats(self) -> Dict:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        stats = {
            "total_operations": len(self.metrics),
            "successful_operations": sum(1 for m in self.metrics if m.success),
            "failed_operations": sum(1 for m in self.metrics if not m.success),
            "operations": {}
        }
        
        # Group by operation
        for operation in set(m.operation for m in self.metrics):
            op_metrics = self.get_metrics(operation)
            durations = [m.duration_seconds for m in op_metrics]
            
            target = self.TARGETS.get(operation)
            within_target = sum(1 for d in durations if target and d <= target)
            
            stats["operations"][operation] = {
                "count": len(op_metrics),
                "avg_duration": sum(durations) / len(durations) if durations else 0.0,
                "min_duration": min(durations) if durations else 0.0,
                "max_duration": max(durations) if durations else 0.0,
                "target": target,
                "within_target": within_target,
                "target_compliance_rate": within_target / len(durations) if durations else 0.0
            }
        
        return stats
    
    def check_targets(self) -> Dict[str, bool]:
        """Check if all operations meet their performance targets.
        
        Returns:
            Dictionary mapping operation names to whether they meet targets
        """
        results = {}
        
        for operation, target in self.TARGETS.items():
            avg_duration = self.get_average_duration(operation)
            if avg_duration > 0:
                results[operation] = avg_duration <= target
        
        return results
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        logger.info("Performance metrics reset")
    
    def log_summary(self):
        """Log a summary of performance metrics."""
        stats = self.get_stats()
        
        logger.info("=== Performance Summary ===")
        logger.info(f"Total operations: {stats['total_operations']}")
        logger.info(f"Successful: {stats['successful_operations']}")
        logger.info(f"Failed: {stats['failed_operations']}")
        
        for operation, op_stats in stats["operations"].items():
            target = op_stats["target"]
            avg = op_stats["avg_duration"]
            compliance = op_stats["target_compliance_rate"] * 100
            
            status = "✓" if target and avg <= target else "✗"
            
            logger.info(
                f"{status} {operation}: avg={avg:.2f}s, "
                f"target={target}s, compliance={compliance:.1f}%"
            )


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.
    
    Returns:
        Global PerformanceMonitor instance
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def reset_monitor():
    """Reset the global performance monitor."""
    global _global_monitor
    if _global_monitor:
        _global_monitor.reset()
