import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for the RAG system"""
    timestamp: datetime
    query_processing_time: float  # seconds
    document_retrieval_time: float  # seconds
    response_generation_time: float  # seconds
    total_response_time: float  # seconds
    documents_retrieved: int
    documents_used: int
    context_length: int  # estimated tokens
    query_length: int  # characters
    response_length: int  # characters
    similarity_scores: List[float]
    metadata: Optional[Dict[str, Any]] = None

class MetricsTracker:
    """Tracks and stores performance metrics for the RAG system"""
    
    def __init__(self):
        """Initialize the metrics tracker"""
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_timers: Dict[str, float] = {}
        
    def start_timer(self, timer_name: str) -> None:
        """
        Start a timer for measuring performance
        
        Args:
            timer_name (str): Name of the timer
        """
        self.current_timers[timer_name] = time.time()
        logger.debug(f"Started timer: {timer_name}")
        
    def stop_timer(self, timer_name: str) -> float:
        """
        Stop a timer and return the elapsed time
        
        Args:
            timer_name (str): Name of the timer
            
        Returns:
            float: Elapsed time in seconds
        """
        if timer_name not in self.current_timers:
            logger.warning(f"Timer {timer_name} not found")
            return 0.0
            
        elapsed_time = time.time() - self.current_timers[timer_name]
        del self.current_timers[timer_name]
        logger.debug(f"Stopped timer {timer_name}: {elapsed_time:.4f}s")
        return elapsed_time
        
    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """
        Record performance metrics
        
        Args:
            metrics (PerformanceMetrics): Metrics to record
        """
        self.metrics_history.append(metrics)
        logger.debug(f"Recorded metrics: {metrics}")
        
    def get_latest_metrics(self) -> Optional[PerformanceMetrics]:
        """
        Get the most recent performance metrics
        
        Returns:
            Optional[PerformanceMetrics]: Latest metrics or None if no metrics recorded
        """
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]
        
    def get_average_metrics(self, last_n: int = 10) -> Optional[PerformanceMetrics]:
        """
        Get average metrics from the last N records
        
        Args:
            last_n (int): Number of recent records to average
            
        Returns:
            Optional[PerformanceMetrics]: Average metrics or None if no metrics recorded
        """
        if not self.metrics_history:
            return None
            
        # Take the last N records (or all if fewer than N)
        recent_metrics = self.metrics_history[-last_n:]
        
        if not recent_metrics:
            return None
            
        # Calculate averages
        avg_query_processing_time = sum(m.query_processing_time for m in recent_metrics) / len(recent_metrics)
        avg_document_retrieval_time = sum(m.document_retrieval_time for m in recent_metrics) / len(recent_metrics)
        avg_response_generation_time = sum(m.response_generation_time for m in recent_metrics) / len(recent_metrics)
        avg_total_response_time = sum(m.total_response_time for m in recent_metrics) / len(recent_metrics)
        avg_documents_retrieved = sum(m.documents_retrieved for m in recent_metrics) / len(recent_metrics)
        avg_documents_used = sum(m.documents_used for m in recent_metrics) / len(recent_metrics)
        avg_context_length = sum(m.context_length for m in recent_metrics) / len(recent_metrics)
        avg_query_length = sum(m.query_length for m in recent_metrics) / len(recent_metrics)
        avg_response_length = sum(m.response_length for m in recent_metrics) / len(recent_metrics)
        
        # Average similarity scores
        all_similarity_scores = []
        for m in recent_metrics:
            all_similarity_scores.extend(m.similarity_scores)
        avg_similarity_scores = all_similarity_scores if all_similarity_scores else []
        
        # Create average metrics object
        avg_metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            query_processing_time=avg_query_processing_time,
            document_retrieval_time=avg_document_retrieval_time,
            response_generation_time=avg_response_generation_time,
            total_response_time=avg_total_response_time,
            documents_retrieved=int(avg_documents_retrieved),
            documents_used=int(avg_documents_used),
            context_length=int(avg_context_length),
            query_length=int(avg_query_length),
            response_length=int(avg_response_length),
            similarity_scores=avg_similarity_scores
        )
        
        return avg_metrics
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all recorded metrics
        
        Returns:
            Dict[str, Any]: Metrics summary
        """
        if not self.metrics_history:
            return {"message": "No metrics recorded yet"}
            
        total_queries = len(self.metrics_history)
        avg_response_time = sum(m.total_response_time for m in self.metrics_history) / total_queries
        avg_documents_retrieved = sum(m.documents_retrieved for m in self.metrics_history) / total_queries
        
        # Get recent performance
        recent_metrics = self.get_average_metrics(10)
        
        return {
            "total_queries_processed": total_queries,
            "average_response_time": round(avg_response_time, 4),
            "average_documents_retrieved": round(avg_documents_retrieved, 2),
            "recent_performance": asdict(recent_metrics) if recent_metrics else None,
            "tracking_since": self.metrics_history[0].timestamp.isoformat() if self.metrics_history else None
        }
        
    def clear_metrics(self) -> None:
        """Clear all recorded metrics"""
        self.metrics_history.clear()
        self.current_timers.clear()
        logger.debug("Cleared all metrics")
        
    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to a JSON file
        
        Args:
            filepath (str): Path to export file
        """
        try:
            # Convert metrics to JSON-serializable format
            metrics_data = []
            for metric in self.metrics_history:
                metric_dict = asdict(metric)
                metric_dict['timestamp'] = metric_dict['timestamp'].isoformat()
                metrics_data.append(metric_dict)
                
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
            logger.info(f"Exported {len(metrics_data)} metrics to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            raise