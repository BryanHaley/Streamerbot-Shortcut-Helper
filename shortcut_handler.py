import socket
import json
import traceback
import sys
import threading
from time import sleep
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Controller

# These are the keys we want to monitor
# Don't send anything when any of these are pressed
KEY_MONITOR = {
    "LeftShift": False,
    "RightShift": False,
    "LeftCtrl": False,
    "RightCtrl": False,
    "LeftAlt": False,
    "RightAlt": False
}

# IP will always be localhost
UDP_IP = "127.0.0.1"
# Default port if we only care about having a single queue
UDP_DEFAULT_PORT = 5125

# Shortcut to check if we're not pressing any of the monitored keys
def all_balls(): # "All balls" == all zeroes
    if (not KEY_MONITOR["LeftShift"]
        and not KEY_MONITOR["RightShift"]
        and not KEY_MONITOR["LeftCtrl"]
        and not KEY_MONITOR["RightCtrl"]
        and not KEY_MONITOR["LeftAlt"]
        and not KEY_MONITOR["RightAlt"]):
        return True
    return False

# Callback for when a key is pressed
def on_press(key):
    try:
        dummy_test = key.char # We don't care about any "normal" keys
    except AttributeError:
        # Update our key monitor dictionary with the current state of the key
        if key == keyboard.Key.shift:
            KEY_MONITOR["LeftShift"] = True
        elif key == keyboard.Key.shift_r:
            KEY_MONITOR["RightShift"] = True
        elif key == keyboard.Key.ctrl_l:
            KEY_MONITOR["LeftCtrl"] = True
        elif key == keyboard.Key.ctrl_r:
            KEY_MONITOR["RightCtrl"] = True
        elif key == keyboard.Key.alt_l:
            KEY_MONITOR["LeftAlt"] = True
        elif key == keyboard.Key.alt_gr:
            KEY_MONITOR["RightAlt"] = True

# Callback for when a key is released
def on_release(key):
    # Update our key monitor dictionary with the current state of the key
    if key == keyboard.Key.shift:
        KEY_MONITOR["LeftShift"] = False
    elif key == keyboard.Key.shift_r:
        KEY_MONITOR["RightShift"] = False
    elif key == keyboard.Key.ctrl_l:
        KEY_MONITOR["LeftCtrl"] = False
    elif key == keyboard.Key.ctrl_r:
        KEY_MONITOR["RightCtrl"] = False
    elif key == keyboard.Key.alt_l:
        KEY_MONITOR["LeftAlt"] = False
    elif key == keyboard.Key.alt_gr:
        KEY_MONITOR["RightAlt"] = False

# Thread entry point
def listen_for_combo_on_port(port_num):
    # Start listening for shortcuts to queue up over UDP (I would use a Unix socket, but these still aren't available for Windows in Python yet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, port_num)) # Port chosen by CLI arg
    print("Listening on port {}".format(port_num))
    while True:
        try:
            # Check if we got any messages
            data, addr = sock.recvfrom(64)
            
            # Look for a KILL message so we can cleanly exit
            if data.decode('utf_8') == "KILL":
                break
            
            # Otherwise, parse the message as JSON
            try:
                message = json.loads(data)
            except:
                print(traceback.format_exc())
                print("Invalid message {} received".format(data))
                sleep(0.1)
                continue
            print("Received message {} on port {}".format(data, port_num))
            key_combo = message["key_combo"]
            # Wait until special key isn't pressed
            while not all_balls():
                sleep(0.1)
            print("Sending key codes: {}, {}".format(key_combo[0], key_combo[1]))
            # Send key combo
            with keyboard_controller.pressed(KeyCode.from_vk(key_combo[0])):
                if key_combo[1] >= 0:
                    keyboard_controller.press(KeyCode.from_vk(key_combo[1]))
                    sleep(0.025)
                    keyboard_controller.release(KeyCode.from_vk(key_combo[1]))
            
            # Sleep for the timeout duration (makes sure redeems don't get scammed)
            sleep(message["timeout"])
        except:
            print(traceback.format_exc())
            sleep(0.1)
    print("Shutting down listener on port {}".format(port_num))
    sock.close() # Technically, this probably never actually happens since you have to kill this in task manager, but whatever it's UDP

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
        
        # Start listening for key presses
        listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
        listener.start()
        
        # Create keyboard controller for sending key presses
        keyboard_controller = Controller()
        
    except:
        # Something badge happened. Quit
        sys.exit(traceback.format_exc())
        
    # Spawn message listener threads
    threads = []
    for port in udp_ports:
        listener_thread = threading.Thread(target=listen_for_combo_on_port, args=(port,))
        threads += [listener_thread]
        listener_thread.start()
    
    # Make sure all threads are finished
    for thread in threads:
        thread.join()
    
    sys.exit(0)