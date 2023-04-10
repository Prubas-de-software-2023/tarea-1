import socket
import threading
import logging
import os
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

    #Mostrar logs por consola
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logging.getLogger().addHandler(console)

# Configuración del servidor
HOST = '127.0.0.1'  # La dirección IP de la máquina en la que se ejecuta el servidor
PORT = 65432        # Puerto que se utiliza para la comunicación

name = input("Select your name: ")
name_lenght = str(len(name))
obtain_log_files()
logging.info("Se ingresado como: %s", name)

# Creación del socket del cliente
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    def split_message(message):
        num = message.split(':')
        name_length = int(num[0])
        name = num[1][0:name_length]
        return name, message.split(name)[1]
    
    # Función para manejar la recepción de mensajes del cliente
    def receive_thread(conn):
        while True:
            try:
                data = conn.recv(1024)  # Recepción de datos del cliente
                if not data:
                    break
                else:
                    name, message = split_message(data.decode()) #Desempaquetar mensaje
                print(f'{name} dice: {message}') #Mostrar mensaje
                logging.info("Se ha recibido el mensaje") #Guardar en log
            except Exception as ex:
                if(ex.args[0]==10053):
                    logging.info("Se ha cerrado la conexion")
                else:
                    logging.error("Error con la conexion al servidor: %s, porfavor reinicie", str(ex))
                conn.close()
                break
            

    # Función para manejar el envío de mensajes al cliente
    def send_thread(conn):
        while True:
            message = input('')
            if(message != "exit()"):
                while(len(message)>100): #Entrar en caso de error si tiene mas de 100 caracteres
                    print("Su mensaje tiene mas de 100 caracteres!") 
                    message = input('')
                message = name_lenght + ':' + name + message #Empaquetar mensaje
            else:
                conn.close()
                break
            try:
                conn.sendall(message.encode())  # Envío de los datos recibidos de vuelta al cliente
                logging.info("Se ha enviado mensaje")
            except Exception as ex:
                logging.error("Ha ocurrido un error al enviar mensaje %s", str(ex))
            print("Hola soy el send")

    try:
        s.connect((HOST, PORT))  # Conexión al servidor

        # Creación de los hilos para manejar la recepción y envío de mensajes
        receive = threading.Thread(target=receive_thread, args=(s,))
        send = threading.Thread(target=send_thread, args=(s,))

        # Inicio de los hilos
        receive.start()
        send.start()

        # Espera a que los hilos terminen
        receive.join()
        send.join()

        s.close()
    except Exception as ex:
        logging.error("Ha ocurrido un error: %s", str(ex))
