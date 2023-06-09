import socket
import threading
import logging
import sys
import os
import base64
from datetime import date


def obtain_log_files():
    fecha_lista = date.today()
    fecha = str(fecha_lista).split("-")

    if not os.path.isdir(fecha[0]+'/'+fecha[1]):
        os.makedirs(fecha[0]+'/'+fecha[1])

    ###Configurando los archivos log
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename= fecha[0]+'/'+fecha[1]+'/'+'cartola_'+fecha[2]+'.log',
                        filemode='a')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)



# Configuración del servidor

HOST = '127.0.0.1'  # IP donde es ejecutado el servidor
PORT = 65433        # Puerto utilizado

obtain_log_files()

name = input("Select your name: ")
while(":" in name):
    print("Invalid character ':'")
    name = input("Select your name: ")
name_length = str(len(name))
logging.info("Joined as: %s", name)






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
                        decoded_message =  base64.b64decode(data).decode('utf-8')
                        name, message = split_message(decoded_message)
                        print(f'{name} says: {message}')
                        logging.info(f'{name} send message which says: {message}')


                except KeyboardInterrupt:
                    logging.warning('Keyboard Interrump.')
                    pass        
                except socket.error as e:
                    logging.warning(f'Socket Error: {e}')
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
                    if message == 'exit()':
                        print('Connection close.')
                        conn.close()
                        break
                    if len(message) > 100 or len(message) < 1:
                        print("Error: Message must have 1 and 100 characters")
                        continue
                    else:
                        logging.info(f'{name} send message which says: {message}')
                        message = str(name_length) + ':' + name + message
                        encoded_message = base64.b64encode(message.encode('utf-8'))        
                        conn.sendall(encoded_message)

                        



                except KeyboardInterrupt:
                    logging.warning('Keyboard Interrupt.')
                    break        
                except socket.error as e:
                    logging.warning(f'Socket Error: {e}')
                    break        
                except Exception as e:
                    logging.warning(f'Error: {e}')
                    break

                
            conn.close()


        try:
            # Espera de una conexión
            conn, addr = s.accept()
            logging.info(f'Connection sucessfull with {name} and {addr}')
        
        except socket.error as e:
            logging.warning(f'Error to connect client: {e}')
            sys.exit()

        # Hilos para la recepcion y envio de mensajes respectivamente
        receive = threading.Thread(target=receive_thread, args=(conn,))
        send = threading.Thread(target=send_thread, args=(conn,))

        receive.start()
        send.start()

        receive.join()
        send.join()

    except socket.error as e:
        logging.warning(f'Socket Error: {e}')
        sys.exit(1)

    except Exception as e:
        logging.warning(f'Error: {e}')
        sys.exit(1)
