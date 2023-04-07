import socket
import threading


# Configuración del servidor
HOST = '127.0.0.1'  # La dirección IP de la máquina en la que se ejecuta el servidor
PORT = 65432        # Puerto que se utiliza para la comunicación


name = input("Select your name: ")
name_length = str(len(name))


# Creación del socket del servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))  # Asociación del socket a la dirección y puerto especificados
    s.listen()            # Escucha de nuevas conexiones

    # Función para manejar la recepción de mensajes del cliente
    def receive_thread(conn):
        def split_message(message):
            num = message.split(':')
            name_length = int(num[0])
            name = num[1][0:name_length]
            return name, message.split(name)[1]

        while True:
            try:
                data = conn.recv(1024)  # Recepción de datos del cliente
                if not data:
                    break
                else:
                    name, message = split_message(data.decode())
                    print(f'{name} dice: {message}')
            except Exception as e:
                print(f'Error: {e}')
                break

        conn.close()

    # Función para manejar el envío de mensajes al cliente
    def send_thread(conn):
        while True:
            try:
                message = input('')
                message = name_length + ':' + name + message
                conn.sendall(message.encode())  # Envío de los datos recibidos de vuelta al cliente
            except Exception as e:
                print(f'Error: {e}')
                break

        conn.close()

    # Espera de una conexión
    conn, addr = s.accept()
    print('Conexión establecida con', addr)

    # Creación de los hilos para manejar la recepción y envío de mensajes
    receive = threading.Thread(target=receive_thread, args=(conn,))
    send = threading.Thread(target=send_thread, args=(conn,))

    # Inicio de los hilos
    receive.start()
    send.start()

    # Espera a que los hilos terminen
    receive.join()
    send.join()
