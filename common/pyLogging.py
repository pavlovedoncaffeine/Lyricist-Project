# pyLogging.py: Aakash Ravichandran 
# Lyricist: November 2020

import sys
import contextlib
from time import strftime, localtime, asctime

def genLogfileName():
    return strftime("%b-%d-%Y %H%M%S", localtime()) + ".log"

def genTimestamp():
    return strftime("%Y-%m-%d  %H%M%S: ", localtime())


@contextlib.contextmanager
def writeLog(file):
    class Logger:
        def __init__(self, file):
            self.terminal = sys.stdout
            self.log = file
            
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            
        def __getattr__(self, attr):
            return getattr(self.terminal, attr)

    pyLogger = Logger(file)

    _stdout = sys.stdout
    _stderr = sys.stderr

    sys.stdout = pyLogger
    sys.stderr = pyLogger

    try:
        yield pyLogger.log
    finally:
        sys.stdout = _stdout
        sys.stderr = _stderr



