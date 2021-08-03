import socket
import threading
import time

# coding=utf-8
main_host = "192.168.0.100"
main_port = 8888

is_recv = False
switch_pocket = {"com.tencent.minihd.qq": "QQHD", "com.tencent.mobileqq": "QQ",
                 "com.tencent.mm": 'wechat', "com.mfashiongallery.emag":"小米画报"}
pocket_channel = {"com.tencent.mobileqq": "1", "com.tencent.minihd.qq": "2",
                  "com.tencent.mm": "3", "com.mfashiongallery.emag": "4"}
block_pocket = {"com.v2ray.ang": 'v2ray'}
analyze = []


def recv():
    global is_recv
    global data
    global analyze
    lock = threading.Lock()
    recv_socket = socket.socket()
    recv_socket.bind((main_host, main_port))
    recv_socket.listen()
    while True:
        client_conn, address = recv_socket.accept()
        f = open("D:\\log.log", "a", encoding="UTF-8")
        lock.acquire()
        local = time.localtime(time.time())
        data = client_conn.recv(500).decode("UTF-8")
        is_recv = True
        analyze = data.split("&")
        if analyze[0] in switch_pocket.keys():
            print(analyze[0])
            data = data.replace(analyze[0], pocket_channel[analyze[0]])
            analyze[0] = switch_pocket[analyze[0]]
            print(data)
        lock.release()
        temp = str(local.tm_mday) + "号  " + str(local.tm_hour) + ":" + str(local.tm_min) + ":" + str(local.tm_sec)
        temp.replace('\u2022', '')
        print("接收数据" + str(analyze))
        if analyze[0] not in block_pocket.keys():
            f.write(temp + "    " + data.replace("&", "   ") + "  \n")
            f.close()


def send():
    global is_recv, send_socket
    global data
    global analyze
    lock = threading.Lock()
    while True:
        time.sleep(0.1)
        if is_recv and analyze[0] in switch_pocket.values():
            send_socket = socket.socket()
            try:
                send_socket.connect(("192.168.0.101", 8886))
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


t1 = threading.Thread(target=recv)
t2 = threading.Thread(target=send)
t1.start()
t2.start()
