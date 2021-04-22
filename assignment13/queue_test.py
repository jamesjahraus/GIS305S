import queue
import threading
import time
# https://docs.python.org/3/library/queue.html
# https://towardsdatascience.com/dive-into-queue-module-in-python-its-more-than-fifo-ce86c40944ef

# https://betterprogramming.pub/create-zero-point-failure-distributed-tasks-with-python-and-zeromq-e2a20941d85b
# https://zeromq.org/


q = queue.Queue()


def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        time.sleep(5)
        print(f'Finished {item}')
        q.task_done()


# turn-on the worker thread
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()

t1 = time.time()
# send thirty task requests to the worker
for item in range(30):
    q.put(item)
print('All task requests sent\n', end='')

# block until all tasks are done
q.join()
t2 = time.time()
tdelta = t2 - t1
print(tdelta)
print('All work completed')
