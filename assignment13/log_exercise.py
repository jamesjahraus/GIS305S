import arcpy
import logging
import queue
import time
from logging.handlers import QueueHandler, QueueListener

# https://docs.python.org/3/howto/logging-cookbook.html
# https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block
# https://docs.python.org/3/library/logging.handlers.html
# https://docs.python.org/3/library/logging.handlers.html#queuehandler
# https://softwareengineering.stackexchange.com/questions/201580/python-multiprocessing-with-queue-vs-zeromq-ipc

# Currently this logs to stream (warning), file (error).
# Goal is to arcpy.AddMessage() to both the stream and a log file.
# This enables logging to appear on the ArcGIS Pro window.
# queues could be helpful for logging thread info from geoprocessing events occurring on different processes.

# Example of a custom arcpy handler:
# https://gis.stackexchange.com/questions/135920/logging-arcpy-error-messages


que = queue.Queue(-1)
queue_handler = QueueHandler(que)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log', mode='a')
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s"
                              "{'file': %(filename)s 'function': %(funcName)s 'line': %(lineno)s}\n"
                              "%(threadName)s: %(message)s\n")
stream_listener = QueueListener(que, stream_handler)
file_listener = QueueListener(que, file_handler)
root = logging.getLogger()
root.addHandler(queue_handler)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
stream_listener.start()
file_listener.start()

while True:
    root.debug('debug msg')
    time.sleep(1)
    root.info('info msg')
    time.sleep(1)
    root.warning('warning msg')
    time.sleep(1)
    root.error('error msg')
    time.sleep(1)

stream_listener.stop()
file_listener.stop()
