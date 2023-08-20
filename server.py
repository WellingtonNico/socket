import socket
from utils import (
    MESSAGE_TYPE_IDENTIFICATION,
    MESSAGE_TYPE_STRING_DATA,
    PORT,
    get_decoded_data,
    get_local_ip,
    send_message,
    start_receive_thread,
)
import threading


local_ip = get_local_ip()[-1]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ("0.0.0.0", PORT)

server_socket.bind(address)

server_socket.listen(5)

print("Socket ouvindo em: ", local_ip)

while True:
    try:
        print("Aguardando conexão...")

        client_socket, client_address = server_socket.accept()

        while True:
            data = client_socket.recv(1024 * 10)
            if not data:
                print("Cliente saiu sem se identificar...")
                client_socket.close()
            data = get_decoded_data(data)
            if data["message_type"] == MESSAGE_TYPE_IDENTIFICATION:
                print(
                    f'Usuário {data["message_data"]} identificado em {client_address}, iniciando recebimento de mensagens...'
                )
                start_receive_thread(client_socket, data["message_data"])
                break
            else:
                send_message(
                    client_socket,
                    MESSAGE_TYPE_STRING_DATA,
                    "Por gentileza, envie sua identificação",
                )
    except:
        break

print("Encerrando servidor...")
server_socket.close()
