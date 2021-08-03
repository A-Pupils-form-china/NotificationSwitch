import socket
import threading
import time
import PySimpleGUI as sg
import numpy
import json

# coding=utf-8
main_host = socket.gethostbyname(socket.gethostname())
main_port = 8888

is_alive = False
is_recv = False

j_file = open("D:\\notification_switch\\data.txt", 'r')
config = dict(json.load(j_file))
j_file.close()
j_file = open("D:\\notification_switch\\pocket.txt", 'r')
switch_pocket = dict(json.load(j_file))
j_file.close()
# all_pocket = ['com.tencent.minihd.qq', 'com.tencent.mobileqq', 'com.tencent.mm', 'com.mfashiongallery.emag']
# numpy.save("D:\\all_pocket.npy",numpy.array(all_pocket))
all_pocket = list(numpy.load("D:\\notification_switch\\all_pocket.npy").tolist())
j_file = open("D:\\notification_switch\\block_pocket.txt", 'r')
block_pocket = dict(json.load(j_file))
j_file.close()
analyze = []
send_ip = ''
print(switch_pocket)

def recv():
    global is_recv
    global data
    global analyze
    global is_alive
    lock = threading.Lock()
    recv_socket = socket.socket()
    recv_socket.bind((main_host, main_port))
    recv_socket.listen()
    while True:
        client_conn, address = recv_socket.accept()
        if not is_alive:
            break
        f = open("D:\\notification_switch\\log.log", "a", encoding="UTF-8")
        lock.acquire()
        local = time.localtime(time.time())
        data = client_conn.recv(500).decode("UTF-8")
        is_recv = True
        analyze = data.split("&")
        if analyze[0] not in all_pocket:
            print("增加")
            all_pocket.append(analyze[0])
        if analyze[0] in switch_pocket.keys():
            data = data.replace(analyze[0], str(switch_pocket[analyze[0]][0]))
            analyze[3] = analyze[0]
            analyze[0] = switch_pocket[analyze[0]][1]
            print(analyze[0])
            print(switch_pocket.values())
        lock.release()
        temp = str(local.tm_mday) + "号  " + str(local.tm_hour) + ":" + str(local.tm_min) + ":" + str(local.tm_sec)
        temp.replace('\u2022', '')
        print("接收数据" + str(analyze))
        if analyze[0] not in block_pocket.keys():
            f.write(temp + "    " + data.replace("&", "   ") + "  \n")
            f.close()
    print("thread1 exit")


def send():
    global is_recv, send_socket
    global data
    global analyze
    global is_alive
    lock = threading.Lock()
    while True:
        time.sleep(0.1)
        if not is_alive:
            break
        if is_recv and analyze[3] in switch_pocket.keys():
            send_socket = socket.socket()
            try:
                send_socket.connect((send_ip, 8886))
            except:
                print("出错")
                data = ""
                is_recv = False
            else:
                lock.acquire()
                send_socket.send(data.encode("UTF-8"))
                print("发送数据" + data)
                data = ""
                is_recv = False
                send_socket.close()
                lock.release()
    print("thread2 exit")


def main():
    global is_alive
    global listen_ip
    global send_ip
    t1 = threading.Thread(target=recv)
    t2 = threading.Thread(target=send)
    lock = threading.Lock()
    column1 = [[sg.T("selected_application")],
               [sg.Listbox(values=list(switch_pocket.items()), size=(0, 5), right_click_menu=['right', ['删除']],
                           key="list1")],
               [sg.B("添加转发应用")]]
    column2 = [[sg.T("blocked_application")],
               [sg.Listbox(values=list(block_pocket.items()), size=(0, 5), right_click_menu=['right', ['移除']],
                           key='list2')],
               [sg.B("添加封禁应用")]]
    layout = [[sg.T("本机IP:" + socket.gethostbyname(socket.gethostname()))],
              [sg.Col(column1), sg.Col(column2)],
              [sg.T("接收端ip："), sg.I("192.168.0.101", key='send_ip')],
              [sg.T("服务未开启", key="status")],
              [sg.B("开始")]]
    window = sg.Window("主机端", layout)
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WINDOW_CLOSED:
            window.close()
            jfile = open("D:\\notification_switch\\pocket.txt", 'w')
            json.dump(switch_pocket, jfile, ensure_ascii=True)
            jfile.close()
            jfile = open("D:\\notification_switch\\block_pocket.txt", 'w')
            json.dump(block_pocket, jfile)
            jfile = open("D:\\notification_switch\\data.txt", 'w')
            json.dump(config, jfile)
            numpy.save("D:\\notification_switch\\all_pocket.npy", numpy.array(all_pocket))
            if t1.is_alive() or t2.is_alive():
                is_alive = False
            break
        if event == "删除":
            if values['list1']:
                lock.acquire()
                del switch_pocket[values['list1'][0][0]]
                window['list1'].update(switch_pocket.items())
                lock.release()
        if event == "添加封禁应用":
            add_pocket = []
            for i in all_pocket:
                if i not in block_pocket:
                    add_pocket.append(i)
            if add_pocket:
                window.hide()
                side_layout2 = [[sg.T("请选择要封禁的应用包名：")],
                                [sg.Combo(values=add_pocket, default_value=add_pocket[0], readonly=True, key='select')],
                                [sg.B("确定")]]
                side_window2 = sg.Window("add", side_layout2)
                while True:
                    side_event, side_values = side_window2.read()
                    if side_event == sg.WINDOW_CLOSED:
                        break
                    if side_event == "确定":
                        if side_values['select'] == '':
                            sg.popup("error", "请选择包名")
                        else:
                            lock.acquire()
                            block_pocket.update({side_values['select']: switch_pocket[side_values['select']][1]})
                            lock.release()
                            break
                side_window2.close()
                window.un_hide()
                window['list2'].update(values=block_pocket)
            else:
                sg.popup('error', '全部应用已封禁')
        if event == "添加转发应用":
            window.hide()
            add_pocket = []
            for i in all_pocket:
                if i not in switch_pocket.keys() and i not in block_pocket:
                    add_pocket.append(i)
            choice = True
            fill = False
            if not add_pocket:
                add_pocket.append("none")
                choice = False
                fill = True
            column_layout1 = [[sg.R('选择包名添加', 'radio', default=choice, disabled=not choice, key='choice')],
                              [sg.T("请选择要添加的包名"),
                               sg.Combo(values=add_pocket, default_value=add_pocket[0], readonly=True,
                                        key='select')],
                              [sg.T('请输入添加应用的名称'), sg.I(key="-in-", size=(25, 20))],
                              [sg.B("选择")]]
            column_layout2 = [[sg.R("自行输入包名添加", 'radio', default=fill, key='fill')],
                              [sg.T("请输入包名"), sg.I(key='-pocket-')],
                              [sg.T("请输入名称"), sg.I(key='-name-')],
                              [sg.B("添加")]]
            side_layout1 = [[sg.Col(column_layout1), sg.Col(column_layout2)]]
            side_window1 = sg.Window('add', side_layout1)
            while True:
                side_event, side_values = side_window1.read(timeout=100)
                print(side_event, side_values)
                if side_event == "__TIMEOUT__":
                    if side_values['choice']:
                        side_window1['select'](disabled=False)
                        side_window1['-in-'](disabled=False)
                        side_window1['-pocket-']('')
                        side_window1['-pocket-'](disabled=True)
                        side_window1['-name-']('')
                        side_window1['-name-'](disabled=True)
                    if side_values['fill']:
                        side_window1['select'](disabled=True)
                        side_window1['-in-']('')
                        side_window1['-in-'](disabled=True)
                        side_window1['-pocket-'](disabled=False)
                        side_window1['-name-'](disabled=False)
                if side_event == sg.WINDOW_CLOSED:
                    break
                if side_event == "选择":
                    if side_values['-in-'] != '' and side_values['select'] != '':
                        config['amount'] += 1
                        temp = {side_values['select']: [config['amount'], side_values['-in-']]}
                        switch_pocket.update(temp)
                        print(switch_pocket)
                        break
                    else:
                        sg.popup('error', '请检查是否输入')
                if side_event == '添加':
                    if side_values['-pocket-'] != '' and side_values['-name-'] != '':
                        config['amount'] += 1
                        temp = {side_values['-pocket-']: [config['amount'], side_values['-name-']]}
                        switch_pocket.update(temp)
                        break
                    else:
                        sg.popup("error", '请检查是否输入')
            window['list1'](values=switch_pocket.items())
            side_window1.close()
            window.un_hide()
        if event == '移除':
            lock.acquire()
            if values['list2'] != '':
                del block_pocket[values['list2'][0][0]]
                window['list2'].update(block_pocket.items())
            lock.release()
        if event == '开始':
            if t1.is_alive() and t2.is_alive():
                sg.popup("error", "已经开始运行")
            elif values['send_ip'] == '':
                sg.popup('error', "ip地址填写错误，请重新填写")
            else:
                send_ip = values['send_ip']
                window['status'].update("服务已开启")
                is_alive = True
                if not t2.is_alive():
                    t2.start()
                if not t1.is_alive():
                    t1.start()


main()
