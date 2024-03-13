import multiprocessing
import subprocess
import time

def cpu_intensive_task():
    """Function that performs a CPU-intensive calculation."""
    while True:
        [x*x for x in range(10000)]

def get_cpu_temperature():
    """Reads the CPU temperature."""
    temp_str = subprocess.getoutput("vcgencmd measure_temp")
    return temp_str

def check_for_throttling():
    """Checks if the CPU is throttling."""
    throttle_status = subprocess.getoutput("vcgencmd get_throttled")
    return throttle_status

def monitor_and_run():
    """Monitors CPU temperature and throttling status while running CPU tasks."""
    num_cores = multiprocessing.cpu_count()
    print(f"Starting CPU stress test.csv on {num_cores} cores. Monitoring temperature and throttling status.")

    processes = []
    for _ in range(num_cores):
        p = multiprocessing.Process(target=cpu_intensive_task)
        p.start()
        processes.append(p)

    try:
        start_time = time.time()
        while True:
            current_time = time.time()
            runtime = current_time - start_time
            print(f"Runtime: {runtime:.2f} seconds")
            print(get_cpu_temperature())
            print(check_for_throttling())
            time.sleep(30)  # Wait for 30 seconds before checking temperature and throttling


    except KeyboardInterrupt:
        print("Terminating CPU stress test.csv.")
    finally:
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    monitor_and_run()
