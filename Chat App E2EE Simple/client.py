from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import random, sys, os
from math import gcd
from Crypto.Cipher import AES
import pyaes
import chardet
import hashlib
import hmac
import time

def countPrimitiveRoots(p):
    result=0
    for i in range(2, p, 1):
        if (gcd(i, p) == 1):
            result = i
            return result

def isPrime(n, k):
    if n == 1 or n == 4:
        return False
    elif n == 2 or n == 3:
        return True
    else:
        for i in range(k):             
            # Chọn 1 số ngẫu nhiên trong [2..n-2] Để đảm bảo rằng n luôn lớn hơn 4
            a = random.randint(2, n - 2)
             
            # Fermat nhỏ
            if power(a, n - 1, n) != 1:
                return False                 
    return True

def generateLargePrime(keysize):
   while True:
      num = random.randrange(2**(keysize-1), 2**(keysize))
      if isPrime(num, 3):
        return num

def power(a, n, p):
    res = 1
    a = a % p 

    while n > 0:         
        if n % 2:
            res = (res * a) % p
            n = n - 1
        else:
            a = (a ** 2) % p
            n = n // 2
             
    return res % p

def receive():
    global sA
    global sB
    global indexNameA
    global indexNameB
    global signature
    while True:
        try:
            msg = client_socket.recv(BUFSIZ)

            the_encoding = chardet.detect(msg)['encoding']

            # Kiểm tra enconding
            if (the_encoding == "ascii"):

                # Kiểm tra statement encoding
                if (msg.decode("utf-8")[0]) == "N" and len(msg.decode("utf8")) >= 9:
                    if msg.decode("utf-8")[1] == "," and msg.decode("utf-8")[8] == "$":
                        testWord = "N,FInDEx$"
                        count = len(testWord)
                        indexNameA = ""
                        indexNameB = ""
                        for i in range (count, len(msg.decode("utf8"))):
                            indexNameA += msg.decode("utf8")[count]
                            indexNameB += msg.decode("utf8")[count]
                            count+=1
                
                # Nếu là chữ kí
                elif (msg.decode("utf8")[0]) == "M" and msg.decode("utf8")[1] == "@"  and len(msg) == 68:
                    count = 4
                    signature = ""
                    for i in range (count, len(msg.decode("utf8"))):
                        signature += msg.decode("utf8")[count]
                        count+=1

            #  decrypt
            if (sA != 0):
                sA = str(sA).encode("utf8")
                aes = pyaes.AESModeOfOperationCTR(sA)

                sig = hmac.new(sA, msg, hashlib.sha256).hexdigest()
                sA = int(sA.decode("utf8"))
    
                msg = aes.decrypt(msg)
                the_encoding_test = chardet.detect(msg)['encoding']
                if (the_encoding_test == "ascii"):
                    if (sig == signature):
                        msg_list.insert(tkinter.END,bytes(indexNameA, encoding='utf-8') + msg)
                    else:
                        msg_list.insert(tkinter.END,"Error !!! Can't load message")

            elif sB != 0: # decrypt
                sB = str(sB).encode("utf8")
                aes = pyaes.AESModeOfOperationCTR(sB)

                sig = hmac.new(sB, msg, hashlib.sha256).hexdigest()
                sB = int(sB.decode("utf8"))
                
                msg = aes.decrypt(msg)
                the_encoding_test = chardet.detect(msg)['encoding']
                if (the_encoding_test == "ascii"):
                    if (sig == signature):
                        msg_list.insert(tkinter.END, bytes(indexNameB, encoding='utf-8')+  msg)
                    else:
                        msg_list.insert(tkinter.END,"Error !!! Can't load message")

            # Trao đổi khóa Ato
            elif ((msg.decode("utf-8")) == "Start Pr@tocol"):
                a = generateLargePrime(53)
                p = generateLargePrime(53)
                g = countPrimitiveRoots(p)
                Ato = power(g,a,p)
                client_socket.send(str(p).encode('utf8'))
                client_socket.send(str(g).encode('utf8'))
                client_socket.send(str(Ato).encode('utf8'))

            # nhận khóa B
            elif (msg.decode("utf-8")[0]) == "B" and msg.decode("utf-8")[1] == ",":
                testWord = "B,FInDEx"
                count = len(testWord)
                indexBto = ""
                for i in range (0 , len(testWord)-1):
                    if (testWord[i] == msg.decode("utf-8")[i]):
                        continue
                    else:
                        msg_list.insert(tkinter.END, msg)
                        break
                if (msg.decode("utf-8")[count] >= "0" and msg.decode("utf-8")[count] <= "9"):
                    
                    # lấy khóa chung B
                    for i in range (count, len(msg.decode("utf-8"))):
                        indexBto += msg.decode("utf-8")[i]

                    # Tính toán khóa bí mật chung từ Bto
                    sA = power(int(indexBto),a,p)
                    testlen = str(sA)
                    if (len(testlen) == 15):
                        sA *= 10
                    print(sA)
            
            # Nhận số nguyên tố
            elif msg.decode("utf-8")[0] == "p" and msg.decode("utf-8")[1] == ",":
                testWord = "p,FInDEx"
                count = len(testWord)
                indexp = ""
                for i in range (0 , len(testWord)-1):
                    if (testWord[i] == msg.decode("utf-8")[i]):
                        continue
                    else:
                        msg_list.insert(tkinter.END, msg)
                        break
                if (msg.decode("utf-8")[count] >= "0" and msg.decode("utf-8")[count] <= "9"):
                    for i in range (count, len(msg.decode("utf-8"))):
                        indexp += msg.decode("utf-8")[i]

            # nhận phần tử sinh
            elif msg.decode("utf-8")[0] == "g" and msg.decode("utf-8")[1] == ",":
                testWord = "g,FInDEx"
                count = len(testWord)
                indexg = ""
                for i in range (0 , len(testWord)-1):
                    if (testWord[i] == msg.decode("utf-8")[i]):
                        continue
                    else:
                        msg_list.insert(tkinter.END, msg)
                        break
                if (msg.decode("utf-8")[count] >= "0" and msg.decode("utf-8")[count] <= "9"):
                    for i in range (count, len(msg.decode("utf-8"))):
                        indexg += msg.decode("utf-8")[i]

            # nhận khóa A
            elif msg.decode("utf-8")[0] == "A" and msg.decode("utf-8")[1] == ",":
                testWord = "A,FInDEx"
                count = len(testWord)
                indexAto = ""
                # Kiem tra header msg = A,FInDEx
                for i in range (0 , len(testWord)-1):
                    
                    # Nếu đúng header
                    if (testWord[i] == msg.decode("utf-8")[i]):
                        continue
                    else:
                        # Khong gửi khóa, thì Hiển thị tin nhắn
                        msg_list.insert(tkinter.END, msg)
                        break
                
                # Nếu đúng header kiểm tra chuỗi phía sau
                if (msg.decode("utf-8")[count] >= "0" and msg.decode("utf-8")[count] <= "9"):
                    
                    # gán Ato
                    for i in range (count, len(msg.decode("utf-8"))):
                        indexAto += msg.decode("utf-8")[i]

                    # Tạo khóa riêng B
                    b = generateLargePrime(53)
                    Bto = power(int(indexg),b,int(indexp))

                    # Tính toán bí mật chung từ khóa chung Ato
                    sB = power(int(indexAto),b,int(indexp))

                    # Gửi Bto
                    client_socket.send(str(Bto).encode("utf8"))
                    print(sB)
                    testlen = str(sB)

                    if (len(testlen) == 15):
                        sB *= 10
            else:
                if(msg.decode("utf8")!="N,FInDEx$"):
                    msg_list.insert(tkinter.END, msg.decode("utf-8"))
        except OSError:  # Possibly client has left the chat.
            break

sA = 0
sB = 0
indexNameA=""
indexNameB = ""
signature = ""

def send(event=None):  # event is passed by binders.
    global sA
    global sB
    global the_encoding
    msg = my_msg.get()
    if msg == "{quit}":
        client_socket.close()
        top.quit()
    elif sA != 0:
        sA = str(sA)
        sA = sA.encode("utf8")
        aes = pyaes.AESModeOfOperationCTR(sA)    
        msg = aes.encrypt(msg)

        signature_send = hmac.new(sA, msg, hashlib.sha256).hexdigest()
        signature_send = "M@C:" + signature_send
        signature_send= signature_send.encode("utf8")
        my_msg.set("")  # Clears input field.

        client_socket.send(signature_send)

        client_socket.send(msg)
        sA = int(sA.decode("utf8"))
    elif sB != 0:
        sB = str(sB)
        sB = sB.encode("utf8")
        aes = pyaes.AESModeOfOperationCTR(sB)    
        msg = aes.encrypt(msg)

        signature_send = hmac.new(sB, msg, hashlib.sha256).hexdigest()
        signature_send = "M@C:" + signature_send
        signature_send= signature_send.encode("utf8")

        my_msg.set("")  # Clears input field.

        client_socket.send(signature_send)

        client_socket.send(msg)
        sB = int(sB.decode("utf8"))
    else:
        my_msg.set("")  # Clears input field.

        # Chỉ nói chuyện một mình với server
        client_socket.send(msg.encode('utf8'))

def on_closing(event=None):
    my_msg.set("{quit}")
    send()

top = tkinter.Tk()
top.title("App Chat Project")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Nhập tên của bạn!.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Gửi", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#Ket noi toi server
HOST = '127.0.0.1'
PORT = 33000
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 8092 
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.