import socket
import time
import argparse
import struct
from datetime import datetime

def readFile(filename, length):
    arr = []
    with open(filename, "r+b") as f:
        arr = bytearray(f.read())
    return arr

def receiveReq(serversocket):
    data, address = serversocket.recvfrom(10000) # FIX
    req = struct.unpack_from("!cII", data)
    fileName = struct.unpack_from(f"!{req[2]}s", data, offset=9)[0].decode('utf-8')
    print(fileName + " received.")
    return fileName, address

if __name__ == "__main__":

    listArgs = []
    
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int, choices=range(2049, 65537), help='Input port number for sender from ports between 2049 and 65536')
    p.add_argument("-g", "--requester_port", type=int, choices=range(2049, 65537), help='Input requester port for receiver from ports between 2049 and 65536')
    p.add_argument("-r", "--rate", type=int, help='Input rate at which packets are sent')
    p.add_argument("-q", "--seq_no", type=int, help='Input sequence of packet exchange')
    p.add_argument("-l", "--length", type=int, help='Input length of the payload')

    args = p.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.bind((socket.gethostname(), args.port))

    filename, address = receiveReq(server)

    try: 
        byteArr = readFile(filename, args.length)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(0, len(byteArr), args.length):
            packet = byteArr[i:min(i+args.length, len(byteArr))]
            sock.sendto(struct.pack(f"!cII{len(bytes)}s", b'D', args.seq_no, len(byteArr), byteArr), (address, args.port))

            print("Time packet was sent: ", datetime.utcnow())
            print("Requester IP: ", address)
            print("Sequence num: ", args.seq_no)
            print("Payload: ", packet.decode('utf-8')[:min(len(packet), 4)]) # in case packet len < 4
            print()
            args.seq_no += len(packet)
            time.sleep(1.0 / args.rate)

        sock.sendto(struct.pack(f"!cII",b'E',0,0), (address, args.port))

        print("Time end packet was sent: ", datetime.utcnow())
        print("Requester IP: ", address)
        print("Sequence num: ", args.seq_no)
        print("Payload: ", packet.decode('utf-8')[:min(len(packet), 4)]) # in case packet len < 4

    except: # in case the file does not exist with the sender

        sock.sendto(struct.pack(f"!cII",b'E',0,0), (address, args.port))
        print("Time end packet was sent: ", datetime.utcnow())
        print("Requester IP: ", address)
        print("Sequence num: ", args.seq_no)
        print("Payload: ", packet.decode('utf-8')[:min(len(packet), 4)]) # in case packet len < 4

    server.close()



