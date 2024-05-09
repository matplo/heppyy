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
        self.level = level
        self.console = console

        # Include the PID in the log filename
        self.log_file = f"{os.path.splitext(log_file)[0]}_{os.getpid()}{os.path.splitext(log_file)[1]}"

        # Create a formatter
        # formatter = logging.Formatter('%(asctime)s name=%(name)-12s level=%(levelname)-8s module=%(module)s func=%(funcName)s: %(message)s')
        self.formatter = logging.Formatter('%(levelname)-8s: %(message)s #[%(asctime)s %(filename)s:%(lineno)d %(funcName)s]')

        # Create a handler for the file
        self.file_handler = logging.FileHandler(self.log_file, mode='w')
        self.file_handler.setLevel(self.level)
        self.file_handler.setFormatter(self.formatter)

        # Create a logger
        self.logger = logging.getLogger()
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.file_handler)

        # If console is True, create a handler for the console
        if self.console:
          self.enable_console()

    def set_formatter_string(self, s):
        self.formatter = logging.Formatter(s)
        self.file_handler.setFormatter(self.formatter)
        if hasattr(self, 'console_handler'):
            self.console_handler.setFormatter(self.formatter)
            
    def set_complex_formatter(self):
        s = '%(asctime)s name=%(name)-12s level=%(levelname)-8s file=%(filename)s:%(lineno)d module=%(module)s func=%(funcName)s: %(message)s'
        self.set_formatter_string(s)

    def set_simple_formatter(self):
        s = '%(message)s #[%(asctime)s %(filename)s:%(lineno)d %(funcName)s]'
        self.set_formatter_string(s)
        
    def enable_console(self):
        if hasattr(self, 'console_handler'):
            self.logger.critical('Console handler already exists')
            return
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)
        self.set_level(self.level)
        self.console = True

    def disable_console(self):
        if hasattr(self, 'console_handler'):
            self.logger.removeHandler(self.console_handler)
            del self.console_handler
            self.console = False
                        
    def set_level(self, level):
        self.level = level
        self.logger.setLevel(self.level)
        self.file_handler.setLevel(self.level)
        if hasattr(self, 'console_handler'):
          self.console_handler.setLevel(self.level)

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