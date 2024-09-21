import multiprocessing
from processes.processes import monitor_popup, print_from_queue

# Main function to start both processes
if __name__ == "__main__":
    # Create a multiprocessing Queue
    queue = multiprocessing.Queue()

    # Create the Producer and Consumer processes
    producer_process = multiprocessing.Process(target=monitor_popup, args=(queue,))
    consumer_process = multiprocessing.Process(target=print_from_queue, args=(queue,))

    # Start both processes
    producer_process.start()
    consumer_process.start()

    # Wait for both processes to complete
    producer_process.join()
    consumer_process.join()
