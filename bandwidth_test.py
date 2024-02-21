import serial
import time
import sys

def test_bandwidth(write_port, read_port, baud_rate, data_size):
    """
    Test bandwidth between two serial ports.

    This function tests the bandwidth by writing and reading a specific amount of data
    between two serial ports at a given baud rate. It calculates and prints the
    bandwidth, duration of the transfer, and efficiency of the transfer.

    @param write_port: The serial port to write data.
    @param read_port: The serial port to read data.
    @param baud_rate: Baud rate for both serial ports.
    @param data_size: Size of data to write in bytes.
    """
    try:
        # Initialize serial ports with context manager to ensure proper closure
        with serial.Serial(write_port, baud_rate, timeout=1) as writer, \
                serial.Serial(read_port, baud_rate, timeout=1) as reader:

            # Generate test data as a sequence of bytes
            data = bytes([x % 256 for x in range(data_size)])

            # Flush any existing data in the buffers
            reader.flushInput()
            writer.flushOutput()

            # Start timing the data transfer
            start_time = time.time()
            writer.write(data)
            writer.flush()  # Ensures data is physically sent out before reading
            read_data = reader.read(data_size)
            end_time = time.time()

            # Check if the written data matches the read data
            if read_data != data:
                print("Data integrity check failed: Received data does not match sent data.")
                print(f"Amount data sent: {len(data)}, data received: {len(data)}")
                return

            # Calculate and print bandwidth, duration, and efficiency
            duration = end_time - start_time
            bandwidth = (data_size * (8+2)) / duration  # Plus 2 bits to account for the serial start/stop bits
            efficiency = (bandwidth / baud_rate) * 100  # percentage

            print(
                f"Transfer Successful - "
                f"Bandwidth: {bandwidth / 1000:.0f} kbps, "
                f"Duration: {duration:.2f} s, "
                f"Efficiency: {efficiency:.2f}%\n")
            time.sleep(0.2)  # Short delay to stabilize serial communications
    except Exception as e:
        print(f"An error occurred at baud rate {baud_rate}: {e}")


if __name__ == "__main__":
    # Define baud rates and serial ports to test
    baud_rates = [230400, 460000, 1000000, 1500000]
    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']

    # Loop through each baud rate
    for baud_rate in baud_rates:
        # Generate pairs of ports for testing
        port_pairs = [(ports[i], ports[(i + 1) % len(ports)]) for i in range(len(ports))]
        data_size = int(baud_rate / 8)  # Calculate data size based on baud rate

        # Test each pair of ports
        for write_port, read_port in port_pairs:
            print(
                f"Testing - Writer: {write_port}, Reader: {read_port}, Baud Rate: {baud_rate / 1000}kbps, Data Size: {data_size * 8 / 1000}kb")
            test_bandwidth(write_port, read_port, baud_rate, data_size)
