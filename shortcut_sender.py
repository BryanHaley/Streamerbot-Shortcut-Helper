import socket
import json
import sys
import traceback
from time import sleep

UDP_IP = "127.0.0.1"
UDP_PORT = 5125

if __name__ == "__main__":
    # Port override. This allows us to have multiple queues for each redeem
    try:
        UDP_PORT = int(sys.argv[1])
    except:
        print(traceback.format_exc())
    
    # Make sure we have the minimum number of arguments
    if len(sys.argv) < 4:
        sys.exit("ERROR: Must specify a port and two keycodes to use!")
    
    while True: # If 'repeater' is enabled for testing, keep doing this over and over again
        try:
            # Build message
            message = str.encode(json.dumps({
                "key_combo": [int(sys.argv[2]), int(sys.argv[3])],
                "timeout": float(sys.argv[4]) if len(sys.argv) >= 5 else 0.1
                }))
            # Send message
            print("Sending {} to {}:{}".format(message, UDP_IP, UDP_PORT))
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message, (UDP_IP, UDP_PORT))
            
            # Determine if we want to break or sleep and repeat depending on CLI arg
            if not (len(sys.argv) >= 6 and sys.argv[5] == "repeater"):
                break
            else:
                sleep(2 if len(sys.argv) < 7 else int(sys.argv[6]))
        except:
            print(traceback.format_exc())
    
    sys.exit(0)