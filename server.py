import socket
import threading
import logging
import sys
import os
import base64
# Configuración del servidor

HOST = '127.0.0.1'  # IP donde es ejecutado el servidor
PORT = 65432        # Puerto utilizado

name = input("Select your name: ")
name_length = str(len(name))

if os.path.exists("server.log"):
    os.remove("server.log")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('server.log', mode='a'),
    ]
)



# Creación del socket del servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))  
        s.listen()            

        def split_message(message):
            num = message.split(':')
            name_length = int(num[0])
            name = num[1][0:name_length]
            return name, message.split(name)[1]
        
        # Recepción de mensajes desde el cliente
        def receive_thread(conn):
            while True:
                try:
                    data = conn.recv(1024)  
                    if not data:
                        break
                    else:
                        decoded_message = base64.b64decode(data)
                        name, message = split_message(decoded_message)
                        print(f'{name} dice: {message}')
                        logging.info(f'{name} ha enviado un mensaje que dice: {message}')


                except KeyboardInterrupt:
                    logging.warning('Interrupción de teclado detectada.')
                    pass        
                except socket.error as e:
                    logging.warning(f'Error de socket: {e}')
                    break
                except Exception as e:
                    logging.warning(f'Error: {e}')
                    break


            conn.close()

        # Envio de mensajes hacia el cliente
        def send_thread(conn):
            while True:
                try:
                    message = input('')
                    if len(message) > 100 or len(message) < 1:
                        print("Error: la longitud del mensaje debe ser entre 1 y 100 caracteres.")
                        continue
                    else:
                        logging.info(f'{name} ha enviado un mensaje que dice: {message}')
                        message = str(name_length) + ':' + name + message
                        encoded_message = base64.b64encode(message)        
                        conn.sendall(encoded_message)

                        
                    if message == 'exit()':
                        print('Se ha terminado la conexión.')
                        break


                except KeyboardInterrupt:
                    logging.warning('Interrupción de teclado detectada.')
                    pass        
                except socket.error as e:
                    logging.warning(f'Error de socket: {e}')
                    break        
                except Exception as e:
                    logging.warning(f'Error: {e}')
                    break

                
            conn.close()


        try:
            # Espera de una conexión
            conn, addr = s.accept()
            logging.info(f'Conexión establecida entre {name} y {addr}')
        
        except socket.error as e:
            logging.warning(f'Error al conectar con el cliente: {e}')
            sys.exit()

        # Hilos para la recepcion y envio de mensajes respectivamente
        receive = threading.Thread(target=receive_thread, args=(conn,))
        send = threading.Thread(target=send_thread, args=(conn,))

        receive.start()
        send.start()

        receive.join()
        send.join()

    except socket.error as e:
        logging.warning(f'Error de socket: {e}')
        sys.exit(1)

    except Exception as e:
        logging.warning(f'Error: {e}')
        sys.exit(1)
