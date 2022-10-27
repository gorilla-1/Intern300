import socket
import threading
import time
import serial
import datetime

lock = threading.Lock()
onMsg = [b'\xA0\x01\x01\xA2', b'\xA0\x02\x01\xA3']
offMsg = [b'\xA0\x01\x00\xA1', b'\xA0\x02\x00\xA2']
statMsg = b'\xFF'
# statik_172.20.10.49remote

serialPort = serial.Serial('COM10', 9600)
state = [0, 0]
onOffStr = ['Off', 'On']

PORT = 8888
# ipv4 address for server
SERVER = socket.gethostbyname(socket.gethostname())
# address stored
ADDRESS = (SERVER, PORT)
print(ADDRESS)
# encode decode format(will it be necessary?)
FORMAT = "utf-8"
# list that contains clients connected
clients, names = [], []
# new socket for server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDRESS)


def get_log(log):
    print(log)
    with open("C:/Relay_Application/Relay_Server/relay_log.txt", "a+") as logs:
        logs.write(str(log))


def read_from_port(ser):
    connected = 1
    global is_ch1
    global is_ch2
    global onoff
    while connected == 1:
        try:
            chars = ser.readline()
            a = chars.split()
            if len(a) == 2:
                n = {b'CH1:': 1, b'CH2:': 2}.get(a[0], 0)
                onoff = {b'OFF': 0, b'ON': 1}.get(a[1], 0)
                if n > 0:
                    message = f"Relay {n} = {onOffStr[onoff]}"
                    print(message)
                    if n == 1 and onoff == 0:
                        is_ch1 = False
                    elif n == 1 and onoff == 1:
                        is_ch1 = True
                    if n == 2 and onoff == 0:
                        is_ch2 = False
                    elif n == 2 and onoff == 1:
                        is_ch2 = True
                    state[n-1] = onoff

            elif len(chars) > 0:
                print('Relay', chars)
        except:
            print('Relay: terminated')
            connected = 0



# relay status
def check_status():
    serialPort.write(statMsg)
    time.sleep(0.5)


def handle(conn, addr, name):
    print(f"new connection {addr}")
    connected = True
    tmp = ''
    message_to_client = ''

    while connected:
        # receive message
        try:
            message_from_client = conn.recv(1024).decode(FORMAT)
            date_time = "{}".format(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            if message_from_client == 'rly1':
                tmp = 1
                message_to_client = switch(tmp - 1, date_time)

            elif message_from_client == 'rly2':
                tmp = 2
                message_to_client = switch(tmp - 1, date_time)

            elif message_from_client == 'cls_port':
                # close connection
                message_to_client = f"{addr} {name} left "
                connected = False
                clients.remove(conn)

            message = f"{name}: {message_to_client}"
            lock.acquire()
            get_log(message)
            lock.release()
            for client in clients:
                client.send(message.encode(FORMAT))

        except :
            clients.remove(conn)
            connected = False
            pass


thread_port = threading.Thread(target=read_from_port, args=(serialPort,))
thread_port.start()


def switch(ch, date_time):

    if state[ch]:
        serialPort.write(offMsg[ch])
        status_msg = f"{date_time}: Relay {ch+1} set off\n"
        state[ch] = 0
        time.sleep(0.1)
    else:
        serialPort.write(onMsg[ch])
        status_msg = f"{date_time}: Relay {ch+1} set on\n "
        state[ch] = 1
        time.sleep(0.1)
    return status_msg


def connect_to_serv():
    print("server working on " + SERVER)

    while True:
        server.listen()
        conn, addr = server.accept()
        conn.send("name: ".encode(FORMAT))
        name = conn.recv(1024).decode(FORMAT)
        names.append(name)

        clients.append(conn)
        print(f"Individual :{name}")
        check_status()
        if conn.recv(1024).decode(FORMAT) == 'receive_stats':
            current_msg = str(state)
            conn.send(current_msg.encode(FORMAT))
        if conn.recv(1024).decode(FORMAT) == 'last_logs':
            with open("C:/Relay_Application/Relay_Server/relay_log.txt", "r") as logs:
                logs.seek(0)
                log_lines = str(logs.readlines()[-10:])
                conn.send(log_lines.encode(FORMAT))

        thread = threading.Thread(target=handle, args=(conn, addr, name))
        thread.start()
        print(f"active connections {threading.activeCount()-2}")


connect_to_serv()
server.close()
serialPort.close()