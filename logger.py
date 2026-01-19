"""
Logging utilities for metafield operations.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "shopify_metafield",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger for metafield operations.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


class MetafieldOperationLogger:
    """Logger wrapper for metafield operations."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize operation logger.
        
        Args:
            logger: Optional logger instance (creates default if not provided)
        """
        self.logger = logger or setup_logger()
    
    def log_write_attempt(
        self,
        product_id: str,
        namespace: str,
        key: str,
        value_type: str,
        metafield_type: str
    ):
        """Log metafield write attempt."""
        self.logger.info(
            f"Writing metafield: product={product_id}, "
            f"namespace={namespace}, key={key}, "
            f"value_type={value_type}, metafield_type={metafield_type}"
        )
    
    def log_write_success(
        self,
        product_id: str,
        namespace: str,
        key: str
    ):
        """Log successful metafield write."""
        self.logger.info(
            f"✓ Successfully wrote metafield: product={product_id}, "
            f"namespace={namespace}, key={key}"
        )
    
    def log_write_error(
        self,
        product_id: str,
        namespace: str,
        key: str,
        error: str
    ):
        """Log metafield write error."""
        self.logger.error(
            f"✗ Failed to write metafield: product={product_id}, "
            f"namespace={namespace}, key={key}, error={error}"
        )
    
    def log_definition_fetch(
        self,
        namespace: str,
        key: str,
        found: bool
    ):
        """Log metafield definition fetch."""
        status = "found" if found else "not found"
        self.logger.debug(
            f"Metafield definition {status}: namespace={namespace}, key={key}"
        )
    
    def log_type_transformation(
        self,
        original_value: Any,
        transformed_value: str,
        metafield_type: str
    ):
        """Log value transformation."""
        self.logger.debug(
            f"Value transformation: {type(original_value).__name__} → "
            f"{metafield_type} = {transformed_value[:100]}"
        )
