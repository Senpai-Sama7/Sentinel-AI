# core/executor.py

import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Any, Callable, Coroutine, TypeVar, ParamSpec
import functools
import logging

# Use modern Python typing for generic functions to ensure full type safety.
P = ParamSpec('P')
T = TypeVar('T')

class ParallelExecutor:
    """
    A robust parallel task executor supporting thread and process pools.
    This is essential for running synchronous, blocking code (both I/O-bound and
    CPU-bound) in an asyncio application without blocking the event loop.
    """
    def __init__(self, max_threads: int = 8, max_processes: int = 4):
        """
        Initializes the thread and process pools.

        Args:
            max_threads: The maximum number of worker threads for I/O-bound tasks.
                         This is typically related to the number of concurrent I/O
                         operations the system can handle.
            max_processes: The maximum number of worker processes for CPU-bound tasks.
                           This is typically related to the number of CPU cores available.
        """
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="io_worker")
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        logging.info(f"ParallelExecutor initialized with {max_threads} threads and {max_processes} processes.")

    async def run_in_thread(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Runs a synchronous, I/O-bound function in the thread pool.
        
        Example: Reading a large file from disk synchronously.
        """
        loop = asyncio.get_running_loop()
        # functools.partial is used to create a new function with the arguments
        # already "baked in," which is the standard way to pass args to run_in_executor.
        return await loop.run_in_executor(
            self.thread_pool, functools.partial(func, *args, **kwargs)
        )

    async def run_in_process(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Runs a synchronous, CPU-bound function in the process pool.
        This is critical for tasks that perform heavy computation and would
        otherwise lock up the Python Global Interpreter Lock (GIL).
        
        Example: Image processing, complex mathematical calculations.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self.process_pool, functools.partial(func, *args, **kwargs)
        )

    def shutdown(self):
        """Gracefully shuts down the thread and process pools."""
        logging.info("Shutting down parallel executors...")
        # The 'wait=True' argument ensures that all pending tasks are completed
        # before the shutdown proceeds.
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logging.info("Parallel executors shut down successfully.")
