import subprocess


def transfer_file_to_rpi(file_path, rpi_ip, rpi_user, rpi_port=2022):
    """
    Transfers a file to a Raspberry Pi using scp over a specified SSH port.

    :param file_path: Path to the file to transfer.
    :param rpi_ip: IP address of the Raspberry Pi.
    :param rpi_user: Username on the Raspberry Pi.
    :param rpi_port: SSH port on the Raspberry Pi.
    """
    destination_path = f"{rpi_user}@{rpi_ip}:/home/{rpi_user}/"

    # Use the -P option for port with scp
    print(f"Transferring {file_path} to {destination_path}")
    subprocess.run(["scp", "-P", str(rpi_port), file_path, destination_path])


if __name__ == "__main__":
    file_path = "large_file.testFile"  # Update this to the path of your file
    rpi_ip = "192.168.15.10"  # Raspberry Pi IP address
    rpi_user = "rc"  # Raspberry Pi username
    rpi_port = 2022  # SSH port used by the Raspberry Pi
    transfer_file_to_rpi(file_path, rpi_ip, rpi_user, rpi_port)