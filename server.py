import socket
import pyautogui
from threading import Thread
import cv2
from PIL import ImageGrab
from ctypes import windll
import numpy as np
import pickle
import struct
import sys
from time import sleep
SCREEN_WIDTH, SCREEN_HEIGHT = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)


IP = "0.0.0.0"
PORT = 8080

global command_list
command_list = []


def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False

def mouse_control(cmd):
    mouse_list = cmd.split("|")[-1].split(",")
    mouse_x = float(mouse_list[0])
    mouse_y = float(mouse_list[1])
    x = mouse_x * SCREEN_WIDTH / 100
    y = mouse_y * SCREEN_HEIGHT / 100
    print(mouse_x, mouse_y)
    pyautogui.moveTo(x,y)
    

def keyboard_control(cmd):
    press_key = cmd.split("|")[-1].strip()
    pyautogui.press(press_key)

def show_video(cmd, client_socket):
    connection = client_socket.makefile('wb')
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    print("Starting video...")
    while True:
        img = ImageGrab.grab(bbox=(0,0, SCREEN_WIDTH, SCREEN_HEIGHT))
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame,0)
        size = len(data)

        client_socket.sendall(struct.pack(">L", size) + data)


def main():

    if not is_admin():
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)   

    
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.bind((IP,PORT))
    my_socket.listen()
    print("Server is up and running...")
    client_socket, addr = my_socket.accept()
    print("New client accepted...")
    windll.user32.BlockInput(True)
    global command_list
    command_list = []
    while True:
        try:
            data = client_socket.recv(240).decode()
        except ConnectionResetError:
            print("The client disconnected...")
            client_socket, addr = my_socket.accept()
            print("New client connected to the server...")
            continue
        command_list = data.split("§")
        counter = 0
        for cmd in command_list:
            if "mouse" in cmd and counter == 0:
                if "mouse" not in command_list:
                    command_list.append("mouse")
                counter += 1
                t1 = Thread(target=mouse_control, args=[cmd])
                t1.start()
            elif "click" in cmd:
                t2 = Thread(target=lambda : pyautogui.click())
                t2.start()
            elif "keyboard" in cmd:
                if "keyboard" not in command_list:
                    pyautogui.FAILSAFE = False
                    pyautogui.PAUSE = 0.0
                    command_list.append("keyboard")
                t3 = Thread(target=keyboard_control, args=[cmd])
                t3.start()
            elif "video" in cmd:
                if "video" not in command_list:
                    command_list.append("video")
                t4 = Thread(target=show_video, args=[cmd,client_socket])
                t4.start()


if __name__ == "__main__":
    main()