import serial
import time
import sys


def test_bandwidth(write_port, read_port, baud_rate, data_size):
    """
    Test bandwidth between two serial ports.

    Args:
        write_port (str): The serial port to write data.
        read_port (str): The serial port to read data.
        baud_rate (int): Baud rate for both serial ports.
        data_size (int): Size of data to write in bytes.
    """
    try:
        # Initialize serial ports
        with serial.Serial(write_port, baud_rate, timeout=1) as writer, \
                serial.Serial(read_port, baud_rate, timeout=1) as reader:

            # Generate test data
            data = bytes([x % 256 for x in range(data_size)])  # Generate a pattern

            # Flush any existing data
            reader.flushInput()
            writer.flushOutput()

            # Measure write/read time
            start_time = time.time()
            writer.write(data)
            writer.flush()  # Ensures data is sent out before starting the read
            read_data = reader.read(data_size)
            end_time = time.time()

            # Verify data integrity
            if read_data != data:
                print("Data integrity check failed: Received data does not match sent data.")
                print(f"Amount data sent: {len(data)}, data received: {len(data)}")
                return

            # Calculate bandwidth
            duration = end_time - start_time
            bandwidth = (data_size * 8) / duration  # Convert bytes to bits and calculate bps
            efficiency = (bandwidth / baud_rate) * 100  # Calculate efficiency as a percentage

            print(
                f"Transfer Successful - "
                f"Bandwidth: {bandwidth / 1000:.0f} kbps, "
                f"Duration: {duration:.2f} s, "
                f"Efficiency: {efficiency:.2f}%\n")
            time.sleep(0.2)
    except Exception as e:
        print(f"An error occurred at baud rate {baud_rate}: {e}")


if __name__ == "__main__":
    # baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 500000, 1000000, 1500000]
    baud_rates = [230400, 500000, 1000000, 1500000]

    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    for baud_rate in baud_rates:
        # Automatically generate port pairs
        port_pairs = [(ports[i], ports[(i + 1) % len(ports)]) for i in range(len(ports))]
        data_size = int(baud_rate / 8)

        for write_port, read_port in port_pairs:
            print(
                f"Testing - Writer: {write_port}, Reader: {read_port}, Baud Rate: {baud_rate / 1000}kbps, Data Size: {data_size * 8/ 1000}kb")
            test_bandwidth(write_port, read_port, baud_rate, data_size)
