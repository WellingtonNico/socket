import socket
import threading

from utils import MESSAGE_TYPE_IDENTIFICATION, MESSAGE_TYPE_STRING_DATA, PORT, get_local_ip, send_message, start_receive_thread


username = input('Digite seu nome de usuário:\n')

server_ip = get_local_ip()[-1]  # Replace with the server's local IP address
server_port = PORT         # Use the same port number as in the server code
address = (server_ip, server_port)

print('Endereço: ',address)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

send_message(client_socket,MESSAGE_TYPE_IDENTIFICATION,username)
# Start a separate thread for receiving messages

start_receive_thread(client_socket,'servidor')

try:
    while True:
        message = input("Envie uma mensagem:\n")
        send_message(client_socket,MESSAGE_TYPE_STRING_DATA,message)
        if message.lower() == 'exit':
            break
except:
    pass


client_socket.close()
