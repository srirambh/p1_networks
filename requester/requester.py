import socket
import struct
import argparse 
import csv
from datetime import datetime
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

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), args.port))

    with open(args.fileoption, "w+") as f:
        end_sum = ""
        data_txt = ""
        

        senderDict = defaultdict(lambda : "")
        for i in dic[args.fileoption]:
            numPackets = totalBytes = 0
            check = False
            start = datetime.utcnow()
            txt = ""
            temp = bytes(args.fileoption, 'utf-8')
            packet = struct.pack(f"!cII{len(temp)}s", b'R', 0, len(temp), temp)
            sock.sendto(packet, (i[1], i[2]))
            while not check:
                data, address = sock.recvfrom(10000)
                header = struct.unpack_from("!cII",data)
                pack_len = header[2]
                totalBytes += pack_len
                if header[0] != b'E':
                    numPackets += 1
                    payload = struct.unpack_from(f"!{pack_len}s", data, offset=9)[0].decode('utf-8')
                    txt += payload
                    senderDict[header[1]] += "DATA packet\n"
                    senderDict[header[1]] += ("recv time: " + str(datetime.utcnow()) + "\n")
                    senderDict[header[1]] += ("sender addr: " + str(str(i[1]) + ":" + str(i[2])) + "\n")
                    senderDict[header[1]] += ("sequence: " + str(header[1]) + "\n")
                    senderDict[header[1]] += ("length: " + str(pack_len) + "\n")
                    senderDict[header[1]] += ("payload: " + str(payload[:min(len(payload), 4)]) + "\n")
                    senderDict[header[1]] += "\n"
                else:
                    check = True
                    end = datetime.utcnow()
                    end_sum += "End packet\n"
                    end_sum += ("recv time: " + str(datetime.utcnow()) + "\n")
                    end_sum += ("sender addr: " + (str(i[1]) + ":" + str(i[2])) + "\n")
                    end_sum += ("sequence: " + str(header[1]) + "\n")
                    end_sum += ("length: " + str(pack_len) + "\n")
                    end_sum += ("payload: 0\n")
                    end_sum += "\n"

                    end_sum += "Summary\n"
                    end_sum += ("sender addr: " + (str(i[1]) + ":" + str(i[2])) + "\n")
                    end_sum += ("Total Data packets: " + str(numPackets) + "\n")
                    end_sum += ("Total Data bytes: " + str(totalBytes) + "\n")
                    

                    totalTime = (end - start).total_seconds()
                    
                    end_sum += ("Average packets/second: " + str(numPackets/totalTime) + "\n")
                    end_sum += ("Duration of the test: " + str(totalTime * 1000) + "ms\n")
                    end_sum += "\n"

            with open(args.fileoption, "a") as f:
                f.write(txt)
        sorted_dict = defaultdict(int, sorted(senderDict.items()))
        for key in sorted_dict.keys():
            print(senderDict[key])
        print(end_sum)

            

