import subprocess
import time
import platform


# Determine architecture path
arch_map = {
    'amd64': 'x86_64-linux-gnu',
    'aarch64': 'aarch64-linux-gnu',
    'armv7l': 'arm-linux-gnueabihf',
    'i686': 'i686-linux-gnu'
}
ARCH_PATH = arch_map.get(platform.machine(), 'i686-linux-gnu')



def execute_modbus_write(master_port, baud_rate, write_timeout=10, slave_id=3, start_register=500, count=10,
                         values=None):
    """
    Execute Modbus write operation from master to slaves.

    Args:
        master_port (str): Serial port for the master device.
        baud_rate (int): Baud rate for Modbus communication.
        write_timeout (int): Timeout for write operation.
        slave_id (int): Slave ID to target the write operation.
        start_register (int): Starting register address for write operation.
        count (int): Number of registers to write.
        values (list): Values to write to the registers. Length should match 'count'.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    if values is None:
        values = list(range(1, count + 1))  # Default values: 1, 2, 3, ..., count

    modpoll_path = f"./modpoll/{ARCH_PATH}/modpoll"  # Adjust ARCH_PATH as necessary

    command = [
                  modpoll_path,
                  '-b', str(baud_rate),
                  '-o', str(write_timeout),
                  '-p', 'none',
                  '-m', 'rtu',
                  '-a', str(slave_id),
                  '-r', str(start_register),
                  '-c', str(count),
                  master_port
              ] + [str(value) for value in values]

    # print(command)
    # Execute the write operation
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    # Check result
    if result.returncode == 0:
        return True
    else:
        print(f"\tModbus write failed: {result.stderr}", flush=True)
        return False


def execute_modbus_read(master_port, baud_rate, read_timeout=10, slave_id=3, start_register=500, count=10,
                        expected_values=None):
    """
    Execute Modbus read operation from master and verify the values.

    Args:
        master_port (str): Serial port for the master device.
        baud_rate (int): Baud rate for Modbus communication.
        read_timeout (int): Timeout for read operation.
        slave_id (int): Slave ID to target the read operation.
        start_register (int): Starting register address for read operation.
        count (int): Number of registers to read.
        expected_values (list): Expected values to verify against the read results. Length should match 'count'.

    Returns:
        bool: True if the read values match the expected values, False otherwise.
    """
    if expected_values is None:
        expected_values = list(range(1, count + 1))  # Default expected values: 1, 2, 3, ..., count

    modpoll_path = f"./modpoll/{ARCH_PATH}/modpoll"  # Adjust ARCH_PATH as necessary

    command = [
        modpoll_path,
        '-b', str(baud_rate),
        '-o', str(read_timeout),
        '-p', 'none',
        '-m', 'rtu',
        '-a', str(slave_id),
        '-r', str(start_register),
        '-c', str(count),
        '-1',  # Poll only once
        master_port
    ]

    # Execute the read operation
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check result
    if result.returncode == 0:
        # Parse the output to extract the read values
        read_values = []
        for line in result.stdout.split('\n'):
            if '[' in line:  # Assuming modpoll output format
                try:
                    _, value = line.strip().split(':')
                    read_values.append(int(value.strip()))
                except ValueError:
                    pass  # Handle or log parsing errors as necessary

        # Verify the read values against the expected values
        # print(read_values)
        if read_values == expected_values:
            return True
        else:
            print(f"\tRead values do not match expected values. Read: {read_values}, Expected: {expected_values}",
                  flush=True)
            return False
    else:
        print(f"\tModbus read failed: {result.stderr}", flush=True)
        return False


def start_modbus_slave(port, baud_rate, parity='none', mode='rtu', slave_id=3):
    """
    Start a Modbus slave in the background.

    Args:
        port (str): The serial port the Modbus slave should listen on, e.g., '/dev/ttyUSB0'.
        baud_rate (int): The baud rate for the serial connection.
        parity (str): Parity for the serial connection. Default is 'none'.
        mode (str): Modbus mode, either 'rtu' or 'ascii'. Default is 'rtu'.
        slave_id (int): Modbus slave ID. Default is 3.

    Returns:
        subprocess.Popen: The subprocess object for the started slave.
    """
    diagslave_path = f"./diagslave/{ARCH_PATH}/diagslave"

    command = [
        diagslave_path,  # Adjust this path as necessary
        '-m', mode,
        '-a', str(slave_id),
        '-b', str(baud_rate),
        '-p', parity,
        port
    ]
    # print(command)
    slave_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return slave_process


# Start multiple slaves
def start_multiple_slaves(configurations, common_baud_rate):
    """
    Start multiple Modbus slaves based on the provided configurations, applying a common baud rate to all.

    Args:
        configurations (list of dict): A list where each dict contains the arguments for starting a slave, excluding baud_rate.
        common_baud_rate (int): The common baud rate to be used for all slaves.

    Returns:
        list of subprocess.Popen: A list of subprocess objects for the started slaves.
    """
    slaves = []
    for config in configurations:
        # Apply the common baud rate to each slave configuration
        config['baud_rate'] = common_baud_rate
        slave = start_modbus_slave(**config)
        slaves.append(slave)

    time.sleep(1)
    return slaves


def rotate_roles(ports, baud_rate):
    """
    Rotate the master and slave roles among the provided ports.

    Args:
        ports (list): A list of RS485 port identifiers.
    """
    num_ports = len(ports)

    for i in range(num_ports):
        master_port = ports[i]
        slave_ports = ports[:i] + ports[i + 1:]

        print(f"Test {i + 1}: Master = {master_port}, Slaves = {slave_ports}, Baud rate = {baud_rate}")

        # Start slaves
        slave_configurations = [{'port': port, 'slave_id': idx + 1} for idx, port in enumerate(slave_ports)]
        slaves = start_multiple_slaves(slave_configurations, baud_rate)

        # Perform the Modbus write operation from the master
        print("\tTesting write of values", flush=True)
        for y in range(num_ports - 1):
            success = execute_modbus_write(master_port, baud_rate, write_timeout=10, slave_id=y + 1,
                                           start_register=500, count=10, values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            port_for_slave = slave_configurations[y]['port']
            if success:
                print(f"\tWrite operation successful {port_for_slave}", flush=True)
            else:
                print(f"\tWrite operation failed {port_for_slave}", flush=True)

        print("\tTesting read of values", flush=True)
        for y in range(num_ports - 1):
            success = execute_modbus_read(master_port, baud_rate, read_timeout=10, slave_id=y + 1,
                                          start_register=500, count=10, expected_values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            port_for_slave = slave_configurations[y]['port']
            if success:
                print(f"\tRead operation successful and values verified {port_for_slave}", flush=True)
            else:
                print(f"\tRead operation failed or values do not match {port_for_slave}", flush=True)

        # Terminate all slave processes
        for slave in slaves:
            slave.terminate()


# Example usage
if __name__ == "__main__":
    print(platform.machine())
    print(ARCH_PATH)
    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    # ports = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    # baud_rates = [9600]
    # baud_rates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800]
    baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800]

    for baud_rate in baud_rates:
        rotate_roles(ports, baud_rate)
