import logging
import os
from config.settings import LOG_LEVEL

class Logger:
    _logger = None

    @staticmethod
    def get_logger():
        if Logger._logger:
            return Logger._logger

        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger("attention_monitor")
        
        # Prevent logs from being passed to the root logger (avoids double printing)
        logger.propagate = False 

        level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)

        # Clear existing handlers if any (useful during re-initialization)
        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        # File Handler
        file_handler = logging.FileHandler("logs/system.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler 
        # Note: You might want to disable this if you are using a real-time TUI dashboard
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        Logger._logger = logger
        return logger