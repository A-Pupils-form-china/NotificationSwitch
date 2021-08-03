import PySimpleGUI as sg
import socket
layout = [[sg.Combo(values=['emmm', 'emmmm', 'hmmmm'], readonly=True, key='combo'), sg.B("e")],
          [sg.T(socket.gethostbyname(socket.gethostname()))]]
window = sg.Window('test', layout)
while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        break
