import _thread


class EasyThread:
    def __init__(self, target, args=(), kwargs={}, lock_thread=False):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.lock_alloc = _thread.allocate_lock()
        self.lock_thread = lock_thread

    def start(self):
        # Start the thread and store its reference
        self.thread = _thread.start_new_thread(self.run, ())

    def run(self):
        # Run the target function
        self.target(*self.args, **self.kwargs)
        # Mark the thread as finished
        self.thread = None

    def join(self):
        # Busy-wait until the thread is finished
        while self.is_alive():
            pass

    def is_alive(self):
        return self.thread is not None

    def terminate(self):
        # Reset the thread reference to terminate
        self.thread = None

    def lock(self):
        self.lock_alloc.acquire()

    def unlock(self):
        self.lock_alloc.release()

    def __del__(self):
        self.terminate()

    def __enter__(self):
        # Acquire the lock and start the thread
        if self.lock_thread:
            self.lock()
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Wait for the thread to finish and release the lock
        self.join()
        if self.lock_thread:
            self.unlock()
