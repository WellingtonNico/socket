import sys
import json
import socket
import threading
from typing import Any

PORT = 4040

MESSAGE_TYPE_IDENTIFICATION = 0
MESSAGE_TYPE_JSON_DATA = 1
MESSAGE_TYPE_STRING_DATA = 2


class TextColor:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    def get_text(text: str, color: str):
        return f"{color}{text}{TextColor.RESET}"


def clear_input_line():
    sys.stdout.write("\033[F")  # Move cursor up one line
    sys.stdout.write("\033[K")  # Clear line


class MessageData:
    message_type: int
    message_data: str | dict | list

    def __init__(self, message_type, message_data) -> None:
        self.message_data = message_data
        self.message_type = message_type
        pass

    @property
    def is_identification(self):
        return self.message_type == MESSAGE_TYPE_IDENTIFICATION


def send_message(client_socket: socket.socket, message_type, message_data):
    client_socket.send(
        json.dumps(
            {"message_type": message_type, "message_data": message_data}
        ).encode()
    )


class ConnectedClient:
    client_socket: socket.socket
    username: str
    client_address: Any

    def __init__(
        self,
        client_socket: socket.socket,
        client_address: Any,
        username: str,
    ) -> None:
        self.client_address = client_address
        self.client_socket = client_socket
        self.username = username

    def send_message(self, message_data: str):
        send_message(self.client_socket, MESSAGE_TYPE_STRING_DATA, message_data)


def get_local_ip():
    hostname = socket.gethostname()
    ip_list = socket.getaddrinfo(hostname, None, socket.AF_INET)
    local_ips = [
        ip[4][0]
        for ip in ip_list
        if ip[1] == socket.SOCK_STREAM and ip[4][0].startswith("192.168.1.")
    ]
    return local_ips[0]


def get_decoded_data(data: bytes) -> MessageData:
    decodedData = json.loads(data.decode())
    return MessageData(
        message_data=decodedData["message_data"],
        message_type=decodedData["message_type"],
    )


def get_decoded_message(data: bytes):
    m = get_decoded_data(data)
    return m.message_data


def wait_input_and_send_messages(client_socket: socket.socket):
    while True:
        message = input()
        clear_input_line()
        if not message.strip():
            continue
        print(f"{TextColor.get_text('[você]',TextColor.CYAN)} - {message}")
        send_message(client_socket, MESSAGE_TYPE_STRING_DATA, message)


def receive_messages(client_socket: socket.socket, username: str, on_close=None):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print(
                    TextColor.get_text(
                        f"Encerrando conexão de {username}", TextColor.RED
                    )
                )
                client_socket.close()
                if on_close is not None and callable(on_close):
                    on_close(client_socket)
                break
            print(
                f"{TextColor.get_text(f'[{username}]',TextColor.YELLOW)} - {get_decoded_message(data)}"
            )
        except Exception as e:
            print("Erro: ", e)
            break


def start_receive_thread(client_socket: socket.socket, username: str, on_close=None):
    t = threading.Thread(
        target=receive_messages, args=(client_socket, username, on_close)
    )
    t.daemon = True
    t.start()
