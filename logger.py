import logging
import os 
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = None
# Configure logging
def setup_logger(name):
    global logger
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO)

    # Create formatters
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler with rotation
    # Use environment variable for log file path, fallback to default
    env_log_file = os.getenv('LOG_FILE')
    if env_log_file:
        log_file = env_log_file
    else:
        log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

def get_logger(name=""):
    global logger
    if logger is None:
        setup_logger(name or 'LLM Mapping')
    return logger


# # Create a default logger instance
# logger = get_logger('scm_ai_agents')