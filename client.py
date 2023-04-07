import socket
import threading

# Configuración del servidor
HOST = '127.0.0.1'  # La dirección IP de la máquina en la que se ejecuta el servidor
PORT = 65432        # Puerto que se utiliza para la comunicación


name = input("Select your name: ")
name_lenght = str(len(name))

# Creación del socket del cliente
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))  # Conexión al servidor

    def split_message(message):
        num = message.split(':')
        name_length = int(num[0])
        name = num[1][0:name_length]
        return name, message.split(name)[1]
    
    # Función para manejar la recepción de mensajes del cliente
    def receive_thread(conn):
        while True:
            data = conn.recv(1024)  # Recepción de datos del cliente
            if not data:
                break
            else:
                name, message = split_message(data.decode())
            print(f'{name} dice: {message}')
        conn.close()

    # Función para manejar el envío de mensajes al cliente
    def send_thread(conn):
        while True:
            message = input('')
            message = name_lenght + ':' + name + message
            conn.sendall(message.encode())  # Envío de los datos recibidos de vuelta al cliente

    # Creación de los hilos para manejar la recepción y envío de mensajes
    receive = threading.Thread(target=receive_thread, args=(s,))
    send = threading.Thread(target=send_thread, args=(s,))

    # Inicio de los hilos
    receive.start()
    send.start()

    # Espera a que los hilos terminen
    receive.join()
    send.join()
