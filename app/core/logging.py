"""
Logging configuration for the Allervie Analytics Dashboard FastAPI backend.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Set up logging for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(logs_dir, "app.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )  # 10MB max file size, keep 5 backups
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Return the configured logger
    return logger
