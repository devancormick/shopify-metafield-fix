"""
Rate limiting utilities for Shopify API calls.
"""

import time
from typing import Optional
from threading import Lock


class ShopifyRateLimiter:
    """Rate limiter for Shopify API to prevent 429 errors."""
    
    def __init__(
        self,
        requests_per_second: float = 2.0,
        burst_size: int = 40
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst requests allowed
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        self.request_times: list = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limits.
        
        Call this before making an API request.
        """
        with self.lock:
            current_time = time.time()
            
            # Remove requests older than 1 second
            self.request_times = [
                t for t in self.request_times
                if current_time - t < 1.0
            ]
            
            # Check if we're at burst limit
            if len(self.request_times) >= self.burst_size:
                # Wait until oldest request is 1 second old
                oldest_time = min(self.request_times)
                wait_time = 1.0 - (current_time - oldest_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time = time.time()
            
            # Ensure minimum interval between requests
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                time.sleep(wait_time)
            
            # Record this request
            self.last_request_time = time.time()
            self.request_times.append(self.last_request_time)
    
    def reset(self):
        """Reset rate limiter state."""
        with self.lock:
            self.last_request_time = 0.0
            self.request_times.clear()
