#!/usr/bin/python26
# -*- coding:utf-8 -*-

import socket
import base64,hashlib,sys,threading,struct,logging,logging.config
import zmq
import os


def InitWebSocketServer(host = "localhost", port = 12345, backlog = 100):  
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clients = []
    try:  
        sock.bind((host,port)) 
        sock.listen(backlog)  
    except:  
        print("Server does not start, please check the port")  
        print sys.exc_info()
        sys.exit(1)  
    logger.info("accepting ...")
    while True:
        connection,address = sock.accept()
        logger.info("handshake")
        if(handshake(connection) != False):
            clients.append(connection)
            logger.info("do ...")
            #DoRemoteCommand(connection)
            t = threading.Thread(target=DoRemoteCommand,args=(connection,clients,))
            t.start()
        logger.info("do")
  
  
def handshake(client):  
    headers = {}  
    shake = client.recv(1024)  
      
    if not len(shake):  
        return False  
      
    header, data = shake.split('\r\n\r\n', 1)  
    for line in header.split("\r\n")[1:]:  
        key, value = line.split(": ", 1)  
        headers[key] = value  
      
    if(headers.has_key("Sec-WebSocket-Key") == False):  
        print("this socket is not websocket,close")  
        client.close()  
        return False  
      
    szOrigin = headers["Origin"]  
    szKey = base64.b64encode(hashlib.sha1(headers["Sec-WebSocket-Key"] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())  
    szHost = headers["Host"]  
      
    our_handshake = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade:websocket\r\n"\
                    "Connection: Upgrade\r\n"\
                    "Sec-WebSocket-Accept:"+ szKey + "\r\n" \
                    "WebSocket-Origin:" + szOrigin + "\r\n" \
                    "WebSocket-Location: ws://" + szHost + "/WebManagerSocket\r\n" \
                    "WebSocket-Protocol:WebManagerSocket\r\n\r\n"  
                      
    client.send(our_handshake)  
    return True
          
def SendData(pData,client,clients):  
    if(pData == False):  
        return False  
    else:  
        pData = str(pData)  
          
    token = "\x81"  
    length = len(pData)  
    if length < 126:  
        token += struct.pack("B", length)  
    elif length <= 0xFFFF:  
        token += struct.pack("!BH", 126, length)  
    else:  
        token += struct.pack("!BQ", 127, length)  
    pData = '%s%s' % (token,pData)  
    #print pData
    for client in clients:
        try:
            client.send(pData)
        except:
            pass
      
    return True  
  
  
def DoRemoteCommand(connection,clients):  
    while 1:  
      if mu.acquire():
        #szBuf = RecvData(8196,connection)  
        szBuf = receiver.recv()
        #szBuf = '%s服务临时关闭'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        #time.sleep(5)
        if szBuf == False:
            break
            #continue
        print szBuf
        SendData(szBuf,connection,clients)  
        mu.release()




if __name__ == "__main__":
    path=os.path.split(os.path.realpath(__file__))[0]
    logging.config.fileConfig(path+"/log4p.conf")
    logger = logging.getLogger("main")

    try:
            context = zmq.Context()
            receiver = context.socket(zmq.PULL)
            receiver.bind("tcp://*:5558")
            mu=threading.Lock()
            InitWebSocketServer(host = "0.0.0.0", port = 1234)
            receiver.close()
            context.term()
    except:
            sys.exit(1)
