import socket
import time
import argparse
import struct

def readFile(filename, length):
    arr= []
    with open(filename, "rb") as f:
        while (byte := f.read(length)):
            arr.append(byte)
    return arr

def receiveRequest(serversocket):
    data, addr = serversocket.recvfrom(MAX_BYTES)
    request = struct.unpack_from("!cII",data)
    length = request[2]
    fileName = struct.unpack_from(f"!{length}s",data,offset=9)[0].decode('utf-8')
    print("file name recieved : "+fileName)
    return fileName, addr

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port")
    parser.add_argument("-g", "--reqport")
    parser.add_argument("-r", "--rate")
    parser.add_argument("-q", "--seq_num")
    parser.add_argument("-l", "--length")

    args = parser.parse_args()

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    serversocket.bind((socket.gethostname(), int(args.port)))