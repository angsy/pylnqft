# Standard Library Imports
from typing import Any, Callable, Tuple, Type, Union
import os
import socket
import time
import traceback
import subprocess
import sys

dir_program = os.path.split(__file__)[0]
filename_error_log = f".error_log"

def print_cls(disp: str) -> None:
    print(f"\u001B[2J\u001B[0;0H{disp}")

def print_br_green(disp: str) -> None:
    print(f"\u001B[32;1m{disp}\u001B[0m")

def print_br_red(disp: str) -> None:
    print(f"\u001B[31;1m{disp}\u001B[0m")

def error_logger(obj: Callable[[Any], Any]) -> Type[object]:

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return obj(*args, **kwargs)
        except Exception:
            error_information = f"{time.asctime()}\n{traceback.format_exc()}"
            log_writer(data = error_information)

    def log_writer(data: str) -> None:
        try:
            with open(file = f"{dir_program}/{filename_error_log}", mode = "a+") as file_handler:
                file_handler.write(f"{data}\n")
        except Exception:
            print_br_red(
                f"""
                \rAn error occured with information as follow:
                \r{data}
                \rAnother error also occured when writing to error log file.
                """
            )
        else:
            print_br_red(
                f"""
                \rAn error occured.
                \rThe error log file can be viewed at {dir_program}.
                """
            )
        auto_exits()

    def auto_exits() -> None:
        secs = int(10)
        while True:
            auto_exits_disp = f"Auto exits in {secs} seconds."
            print(f"{auto_exits_disp}", end = "", flush = True)
            time.sleep(1)
            print(f"\b" * len(auto_exits_disp) + f" " * len(auto_exits_disp) + f"\b" * len(auto_exits_disp), end = "", flush = True)
            secs -= int(1)
            if secs == int(0):
                break
        sys.exit()

    return wrapper

@error_logger
def main() -> None:
    (file_name, file_data, binary_data) = file_handler()
    address = socket_address()
    link = f"{address[0]}:{address[1]}/{file_name}"
    print(f"\nFile will be temporarily hosted at...")
    print_br_green(f"{link}")
    print(f"Please exits the program after transfer completed.\n")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(address)
    server_socket.listen()
    while True:
        client_socket, client_address = server_socket.accept()
        connection_handler(client_socket, file_name, file_data, binary_data)

def file_handler() -> Tuple[str, Union[str, bytes], bool]:

    while True:
        _file_path = input(f"Full path to the file to be transferred...\n")
        if os.path.isfile(f"{_file_path}") is True:
            break
        else:
            print_br_red(f"File path specified invalid. Please try again.")

    _file_name = os.path.basename(f"{_file_path}")

    try:
        with open(file = f"{_file_path}", encoding = "utf-8", mode = "r") as file_io:
            _file_data = file_io.read()
            _binary_data = False
    except UnicodeDecodeError:
        with open(file = f"{_file_path}", mode = "rb") as file_io:
            _file_data = file_io.read()
            _binary_data = True

    return (_file_name, _file_data, _binary_data)

def socket_address() -> Tuple[str, int]:
    while True:
        _unverified_input = input(f"IP v4 address to listen to...\n")
        verified = True
        _unparsed_input = _unverified_input.split(".")
        ipv4_octets = []
        for data in _unparsed_input:
            try:
                _octet = int(data)
                if _octet >= int(0) and _octet < int(256):
                    ipv4_octets.append(_octet)
                else:
                    verified = False
            except ValueError:
                verified = False
        if len(ipv4_octets) != int(4) or verified == False:
            print_br_red(f"Error in handling the specified address. Please try again.")
        else:
            break
    while True:
        _unverified_input = input(f"Port number to listen to...\n")
        try:
            port_number = int(_unverified_input)
            if port_number >= int(0) and port_number < int(65536):
                break
            else:
                print_br_red(f"Error in handling the specified port number. Please try again.")
        except ValueError:
            print_br_red(f"Error in handling the specified port number. Please try again.")
    return (f"{ipv4_octets[0]}.{ipv4_octets[1]}.{ipv4_octets[2]}.{ipv4_octets[3]}", port_number)

def connection_handler(client_socket: socket.socket, file_name: str, file_data: Union[str, bytes], binary_data: bool) -> None:
    expected_request_uri = f"/{file_name}"
    receiving_buffer = client_socket.recv(1024)
    request = receiving_buffer.decode("utf-8")
    request = request.split(f"\r\n")
    request_line = request[0].split(" ")
    if request_line[0] == "GET" and request_line[1] == expected_request_uri and binary_data == False:
        outgoing_data = f"{request_line[2]} 200 OK\r\nContent-Disposition: attachment; filename={file_name}\r\nContent-Length: {len(file_data)}\r\n\r\n{file_data}"
        client_socket.sendall(outgoing_data.encode("utf-8"))
    if request_line[0] == "GET" and request_line[1] == expected_request_uri and binary_data == True:
        outgoing_data = f"{request_line[2]} 200 OK\r\nContent-Disposition: attachment; filename={file_name}\r\nContent-Length: {len(file_data)}\r\n\r\n".encode("utf-8") + file_data
        client_socket.sendall(outgoing_data)

if __name__ == "__main__":
    if sys.platform.startswith(f"win32"):
        subprocess.run(args = f"", shell = True)
    main()
