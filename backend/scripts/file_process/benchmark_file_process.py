import time
import multiprocessing
from contextlib import contextmanager

import mp_main_one


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

    directory_list = [
        '/Users/rahulduggal/Desktop/test_directory_one',
        '/Users/rahulduggal/Desktop/test_directory_two',
        '/Users/rahulduggal/Desktop/test_directory_three',
        '/Users/rahulduggal/Desktop/test_directory_four',
    ]

    # Run benchmark for the original modular approach
    with timer(f"Original Approach with {num_workers} workers"):
        mp_main_one.main(
            user_directory_file_path = directory_list[0]
        )
        # for fp in directory_list:
        #     mp_main_one.main(
        #         user_directory_file_path = fp
        #     )

    # # Run benchmark for the integrated approach
    # with timer(f"Integrated Approach with {num_workers} workers"):
    #     integrated_main()


if __name__ == "__main__":
    benchmark()
