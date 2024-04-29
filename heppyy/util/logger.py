# logger.py
import logging
import os

# Singleton class for logging
class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_file='heppyy.log', level=logging.INFO, console=True):
        if self._initialized:
            return
        self._initialized = True

        # Include the PID in the log filename
        log_file = f"{os.path.splitext(log_file)[0]}_{os.getpid()}{os.path.splitext(log_file)[1]}"

        # Create a formatter
        # formatter = logging.Formatter('%(asctime)s name=%(name)-12s level=%(levelname)-8s module=%(module)s func=%(funcName)s: %(message)s')
        formatter = logging.Formatter('%(asctime)s name=%(name)-12s level=%(levelname)-8s file=%(filename)s:%(lineno)d module=%(module)s func=%(funcName)s: %(message)s')

        # Create a handler for the file
        self.file_handler = logging.FileHandler(log_file, mode='w')
        self.file_handler.setLevel(level)
        self.file_handler.setFormatter(formatter)

        # Create a logger
        self.logger = logging.getLogger()
        self.logger.setLevel(level)
        self.logger.addHandler(self.file_handler)

        # If console is True, create a handler for the console
        if console:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(level)
            self.console_handler.setFormatter(formatter)
            self.logger.addHandler(self.console_handler)
                
    def set_level(self, level):
        self.logger.setLevel(level)
        self.file_handler.setLevel(level)
        if hasattr(self, 'console_handler'):
          self.console_handler.setLevel(level)

    def get_logger(self, module_name):
        return logging.getLogger(module_name)

    def __getattr__(self, name):
        # If the attribute is a logging method, return the method of the logger
        if name in ['debug', 'info', 'warning', 'error', 'critical']:
          return getattr(self.logger, name)
        else:
          if name in self.__dict__.keys():
            return getattr(self, name)
          else:
            # If the attribute doesn't exist, raise an AttributeError
            raise AttributeError(f"'Logger' object has no attribute '{name}'")