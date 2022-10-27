import os
import socket
import threading
import time
from tkinter import *

state = [0, 0]

PORT = 8888
SERVER = "172.20.10.49"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

if client.recv(1024).decode(FORMAT) == "name: ":
    client.send(os.getlogin().encode(FORMAT))
client.send('receive_stats'.encode(FORMAT))
stat_msg = client.recv(1024).decode(FORMAT)
state = eval(stat_msg)

relay1_name = "Relay 1"
relay2_name = "Relay 2"


def start_read1(is_on):
    if is_on:
        stat_text = f'{relay1_name} is On'
        color = "green"
        img = PhotoImage(file="on.png")
    else:
        stat_text = f'{relay1_name} is Off'
        color = "red"
        img = PhotoImage(file="off.png")
    return (stat_text,color,img)


def start_read2(is_on):
    if is_on:
        stat_text = f'{relay2_name} is On'
        color = "green"
        img = PhotoImage(file="on.png")
    else:
        stat_text = f'{relay2_name} is Off'
        color = "red"
        img = PhotoImage(file="off.png")
    return (stat_text,color,img)


def switch():
    message = 'rly1'
    time.sleep(0.1)
    client.send(message.encode(FORMAT))
# client.send(message.encode(FORMAT))


def switch2():
    message = 'rly2'
    time.sleep(0.1)
    client.send(message.encode(FORMAT))


def receive():
    ch1_on = 'Relay 1 set on'
    ch1_off = 'Relay 1 set off'
    ch2_on = 'Relay 2 set on'
    ch2_off = 'Relay 2 set off'
    while thread_stat:
        try:
            message = client.recv(1024).decode(FORMAT)
            stat_txt = message[22:]
            mylist.config(state=NORMAL)
            mylist.insert(END, message)
            mylist.config(state=DISABLED)
            mylist.see(END)
            if ch1_on in stat_txt:
                relay1_btn.config(image=on)
                my_label.config(text=f"{relay1_name} is on", fg="green")

            elif ch1_off in stat_txt:
                relay1_btn.config(image=off)
                my_label.config(text=f"{relay1_name} is off", fg="red")

            if ch2_on in stat_txt:
                relay2_btn.config(image=on)
                my_label2.config(text=f"{relay2_name} is on", fg="green")

            elif ch2_off in stat_txt:
                relay2_btn.config(image=off)
                my_label2.config(text=f"{relay2_name} is off", fg="red")
        except:
            pass


# Create Object
root = Tk()
w = 600 # width for the Tk root
h = 300 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.minsize(600, 300)
root.maxsize(600, 300)
mylist = Listbox(root, width=50)
mylist.pack(side=RIGHT, fill=Y)

client.send('last_logs'.encode(FORMAT))
logs = eval(client.recv(2048).decode(FORMAT))
for msg in logs:
    mylist.insert(END, msg)

left_frame = Frame(root)
left_frame.pack(side=LEFT)

on = PhotoImage(file="on.png")
off = PhotoImage(file="off.png")


stat_text0, color0, img0 = start_read1(state[0])
stat_text1, color1, img1 = start_read2(state[1])

my_label = Label(root, text=stat_text0, fg=color0, font=("default", 15))
my_label.place(x=50, y=20)
my_label2 = Label(root, text=stat_text1, fg=color1, font=("default", 15))
my_label2.place(x=50, y=120)

relay1_btn = Button(root, image=img0, bd=0, command=switch)
relay1_btn.place(x=50, y=55)
relay2_btn = Button(root, image=img1, bd=0, command=switch2)
relay2_btn.place(x=50, y=155)

# Keep track of the button state on/off
# global is_on
# Define images
thread_stat = True
stats = threading.Thread(target=receive,)
stats.start()
root.mainloop()
client.send('cls_port'.encode(FORMAT))
thread_stat = False
client.close()


