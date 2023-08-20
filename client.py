import socket
import threading

from utils import (
    MESSAGE_TYPE_IDENTIFICATION,
    MESSAGE_TYPE_STRING_DATA,
    PORT,
    TextColor,
    clear_input_line,
    get_local_ip,
    send_message,
    start_receive_thread,
)


username = input("Digite seu nome de usuário:\n")

server_ip = get_local_ip()[-1]

new_ip = input(f"Insira um endereço(padrão {server_ip})")

if new_ip:
    server_ip = new_ip

server_port = PORT
address = (server_ip, server_port)

print("Endereço: ", address)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

send_message(client_socket, MESSAGE_TYPE_IDENTIFICATION, username)
# Start a separate thread for receiving messages

start_receive_thread(client_socket, "servidor")

print("Pode começar enviar mensagens, use CTRL+c para parar:\n")

try:
    while True:
        message = input()
        clear_input_line()
        if not message.strip():
            continue
        print(f"{TextColor.get_text('[você]',TextColor.CYAN)} - {message}")
        send_message(client_socket, MESSAGE_TYPE_STRING_DATA, message)
except:
    pass


client_socket.close()
