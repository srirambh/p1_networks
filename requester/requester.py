import argparse 
import socket
import struct
import csv
from datetime import datetime
from datetime import timedelta
from collections import defaultdict

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int, choices=range(2049, 65537), help='Input port number for receiver from ports between 2049 and 65536')
    p.add_argument("-o", "--fileoption", help='Input file name')
    args = p.parse_args()
    
    dic = {}
    with open("tracker.txt", "r") as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            dic.setdefault(row[0], [])
            dic[row[0]].append([int(row[1]), row[2], int(row[3])])
    

    sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), args.port))

    with open(args.fileoption, "w+") as f:
        for i in dic[args.fileoption]:
            sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
            sock.sendto(struct.pack(f"!cII{len(bytes(args.fileoption, 'utf-8'))}s",
                                    b'R', 0, len(bytes(args.fileoption, 'utf-8')),
                                    bytes(args.fileoption, 'utf-8')), (i[1], i[2]))

            numPackets = totalBytes = 0
            check = False
            start = datetime.utcnow()
            txt = ""
            while not check:
                data, address = sock.recvfrom(10000)
                header = struct.unpack_from("!cII",data)
                pack_len = header[2]
                totalBytes += pack_len
                if header[0] != b'E':
                    numPackets += 1
                    payload = struct.unpack_from(f"!{pack_len}s", data, offset=9)[0].decode('utf-8')
                    txt += payload
                    print("Time packet was received: ", datetime.utcnow())
                    print("Sender's IP address: ", address[0])
                    print("Sender's port number: ", address[1])
                    print("Sequence number: ", header[1])
                    print("Payload length: ", pack_len)
                    print("Payload data: ", payload[:min(len(payload), 4)])
                    print()
                else:
                    check = True
                    end = datetime.utcnow()
                    print("Time packet was received: ", datetime.utcnow())
                    print("Sender's IP address: ", address[0])
                    print("Sender's port number: ", address[1])
                    print("Sequence number: ", header[1])
                    print("Payload length: ", pack_len)
                    print("Payload data: ", payload[:min(len(payload), 4)])
                    print()

                    print("Sender's IP address: ", address[0])
                    print("Sender's port number: ", address[1])
                    print("Sequence num: ", header[1])
                    print("Total number of data packets received: ", numPackets)
                    print("Total number of data bytes received: ", totalBytes)
                    print()

                    totalTime = (end - start).total_seconds()
                    
                    print("Average packets/second: ", numPackets/totalTime)
                    print("Duration of test: ", totalTime, " s")
                
            with open(args.fileoption, "a") as f:
                f.write(txt)

