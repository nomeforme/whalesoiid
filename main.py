import multiprocessing
from processes.processes import monitor_popup, speak_donations, conversation

# Main function to start both processes
if __name__ == "__main__":
    # Create a multiprocessing Queue
    ctx = multiprocessing.get_context('spawn')
    donation_queue = ctx.Queue()
    donation_timeout_event = ctx.Event()

    # Create the Producer and Consumer processes
    dontation_listen_process = ctx.Process(target=monitor_popup, args=(donation_queue, donation_timeout_event))
    donation_speak_process = ctx.Process(target=speak_donations, args=(donation_queue, donation_timeout_event))
    conversation_process = ctx.Process(target=conversation, args=(donation_timeout_event,))

    # Start processes
    dontation_listen_process.start()
    donation_speak_process.start()
    conversation_process.start()

    # Wait for processes to complete
    dontation_listen_process.join()
    donation_speak_process.join()
    conversation_process.join()
