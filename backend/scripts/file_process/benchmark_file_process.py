import time
import multiprocessing
from contextlib import contextmanager

# Your original script functions
from your_original_script import main as original_main
from your_integrated_script import main as integrated_main

@contextmanager
def timer(label: str):
    """Context manager to time code blocks."""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"[{label}] Elapsed time: {end_time - start_time:.2f} seconds")

def benchmark():
    # Adjust the number of cores used in multiprocessing to match your environment
    num_workers = multiprocessing.cpu_count()

    # Run benchmark for the original modular approach
    with timer(f"Original Approach with {num_workers} workers"):
        original_main()

    # Run benchmark for the integrated approach
    with timer(f"Integrated Approach with {num_workers} workers"):
        integrated_main()

if __name__ == "__main__":
    benchmark()
