from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import hashlib
import hmac
import chardet

def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Nhập tên của bạn rồi bắt đầu chat!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    global indexP
    global indexG
    global indexAto
    global tester
    name = client.recv(BUFSIZ).decode("utf8") # nhận tên client

    welcome = 'Xin chào %s! Nếu bạn muốn thoát gõ, {quit} để thoát.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s đã tham gia phòng chat!" % name

    broadcast(bytes(msg, "utf8")) #
    
    clients[client] = name # dict

    if (len(clients) == 1):
        # tester = provider = client 1
        tester=client
        client.send("Start Pr@tocol".encode("utf-8")) # Bắt đầu protocol

        # Chờ P, G, Ato
        indexP=client.recv(BUFSIZ).decode("utf8")
        indexG=client.recv(BUFSIZ).decode("utf8")
        indexAto=client.recv(BUFSIZ).decode("utf8")
    if(len(clients) == 2):
        # khởi tạo, thêm header
        indexP="p,FInDEx" + indexP
        indexG="g,FInDEx" + indexG
        indexAto = "A,FInDEx" + indexAto

        # Gửi P, G cho client 2
        client.send(indexP.encode("utf8"))
        time.sleep(0.25)
        client.send(indexG.encode("utf8"))
        time.sleep(0.25)

        # gửi Ato 1
        client.send(indexAto.encode("utf8"))

        # nhận Bto 1
        indexBto = client.recv(BUFSIZ).decode("utf8")

        indexBto = "B,FInDEx" + indexBto

        # Hoán vị để gửi Bto 
        tester1= client

        client = tester

        client.send(indexBto.encode("utf8"))

        client = tester1

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
                broadcast(msg, name + ": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s đã thoát phòng chat." % name, "utf8"))
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    prefix = "N,FInDEx$" + prefix
    the_encoding = chardet.detect(msg)['encoding']
    if the_encoding == "ascii" and len(msg)==68: # không cần gửi prefix
        if (msg.decode("utf8")[0]=="M" and msg.decode("utf8")[1]=="@"): # ??? gui di chu ki
            for sock in clients:
                sock.send(msg)
        time.sleep(0.1)
    else:
        for sock in clients:
            sock.send(prefix.encode("utf8"))
            sock.send(msg)

indexP = ""
indexG = ""
indexAto = ""

clients = {}
addresses = {}

HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 8092 
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(2)
    print("Chờ kết nối từ các client...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()