import socket
import struct
import pyautogui
import win32api
import keyboard
import time
from threading import Thread
from sys import exit
import pickle
import cv2
from ctypes import windll

#Setting the ip address and chosen port
IP = '192.168.1.101'
PORT = 8080

SCREEN_WIDTH, SCREEN_HEIGHT = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)

#List that contains all the activate commands
command_list = []

#Updating the command list by getting input from the user
def get_commands():
    global command_list
    while True:
        cmd = input("Enter command: ")
        if cmd == "exit-program":
            exit()
        if cmd.startswith("stop"):
            command_list.remove(cmd.split(" ")[-1])
        else:
            command_list.append(cmd)


#This function waiting untiil the command show-video is added and then recieving from the server screenshot of his computer continuously 
def show_video(my_socket):
    while 'show-video' not in command_list:
        time.sleep(0.25)
    message = "video|".zfill(23) + "§"
    my_socket.send(message.encode())
    payload_size = struct.calcsize(">L")
    data = b""
    while True:
        while len(data) < payload_size:
            data += my_socket.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += my_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('ImageWindow', frame)
        cv2.waitKey(1)


#This function send to the server continuously the mouse position - the server using this data to change his mouse position        
def mouse_control(my_socket):
    while "mouse-control" not in command_list:
        time.sleep(0.25)
    mouse_x, mouse_y = pyautogui.position()
    state_left = win32api.GetKeyState(0x01)
    while True:
        a = win32api.GetKeyState(0x01)
        if a != state_left:
            state_left = a
            if a < 0:
                message = "click|".ljust(23) + "§"
                my_socket.send(message.encode())

        elif pyautogui.position() != (mouse_x, mouse_y):
            mouse_x, mouse_y = pyautogui.position()
            x = round(mouse_x / SCREEN_WIDTH * 100, 2)
            y = round(mouse_y / SCREEN_HEIGHT * 100, 2)
            message = "mouse|" + str(x).zfill(8) + "," + str(y).zfill(9) + "§"
            my_socket.send(message.encode())
                
#Sending the server the pressed key - the server press on the key that we send here
def keyboard_control(my_socket):
    while "keyboard-control" not in command_list:
        time.sleep(0.25)
    while True:
        pressed_key = keyboard.read_key()
        message = ("keyboard|" + pressed_key).ljust(23) + "§"
        my_socket.send(message.encode())
        time.sleep(0.2)


        
#The main function - divided to threads fo async functilarity
def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP,PORT))
    print("Connected to the server...")
    global command_list
    t1 = Thread(target=get_commands)
    t1.start()

    t2 = Thread(target=mouse_control, args=[my_socket])
    t2.start()

    t3 = Thread(target=keyboard_control, args=[my_socket])
    t3.start()

    t4 = Thread(target=show_video, args=[my_socket])
    t4.start()

if __name__ == "__main__":
    main()

