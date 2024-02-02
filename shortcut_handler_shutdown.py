import socket
import json
import sys
import traceback
from time import sleep

UDP_IP = "127.0.0.1"
UDP_DEFAULT_PORT = 5125

if __name__ == "__main__":
    # Get port numbers from CLI args
    udp_ports = []
    try:
        if len(sys.argv) == 1:
            # No arguments; just use the default port only
            udp_ports += [UDP_DEFAULT_PORT]
        else:
            for arg in sys.argv:
                try:
                    udp_ports += [int(arg)]
                except:
                    pass

        # Sanity check (can happen if given only non-integer arguments)
        if len(udp_ports) < 1:
            raise Exception("Got invalid CLI args. Specify port numbers separated by a space.")
    
        # Send kill message on all ports
        for port in udp_ports:
            message = str.encode("KILL")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message, (UDP_IP, port))
            
    except:
        sys.exit(traceback.format_exc())
    sys.exit(0)