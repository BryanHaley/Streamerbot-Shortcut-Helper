# Streamerbot Shortcut Helper
This is a collection of scripts to assist with controlling software that can only be interfaced with using keyboard shortcuts from streamerbot.

Requires [Python3](https://www.python.org/downloads/) to be installed, and the [pynput](https://pypi.org/project/pynput/) package to be installed.

## Problem
Many applications (Veadotube Mini, Snap Camera, etc) that are controlled by keyboard shortcuts are interfered with if you are pressing modifier keys like Ctrl, Shift, or Alt. This is fine during normal usage, but if you're trying to trigger events with streamerbot you might be holding one of those keys during gameplay (sprinting, crouching, etc), and cause the event to fail.

## Solution
shortcut_handler.py receives a signal when you want to send a keyboard shortcut through streamerbot, and holds them in a queue until you are no longer pressing Ctrl, Shift, or Alt. This is seamless and allows events to happen uninterrupted with no manual intervention from the streamer.

## Usage
```
pythonw.exe shortcut_handler.py <port numbers>
pythonw.exe shortcut_handler_shutdown.py <port numbers>
pythonw.exe shortcut_sender.py <port number> <keycode 1> <keycode 2> <optional: timeout>
```

For the purposes of demonstration, suppose you have two actions you want to trigger through keyboard shortcuts: activating a vtuber ('P' key), and activating an accessory on the vtuber ('Ctrl+P' key combo).

- Decide how many queues you want, and pick arbitrary numbers for them. Normally, you'd want one queue per action that sends a keyboard shorcut. So, in this scenario, let's pick 5125 for activating the vtuber, and 5126 for activating the accessory. Now we need to tell the shortcut handler to listen on these queues.
  - Create an action that is triggered by Streamerbot opening.
    - Create a sub-action that starts a process. The process should be `pythonw.exe shortcut_handler_shutdown.py 5125 5126`
    - Create another sub-action that starts a process under the previous one. The process should be `pythonw.exe shortcut_handler.py 5125 5126`
    - These two sub-actions shutdown the handler if it's active already, then starts a fresh handler.
    - If you add more queues in the future, you must add the new port numbers to **both** sub-actions.
- Create your actions.
  - In this scenario, for activating the vtuber, we need to create an action triggered by a Twitch redemption. Let's presume we want the vtuber model to appear for 30 seconds, then disappear again.
    - Create a sub-action that starts a process. The process should be `pythonw.exe shortcut_sender.py 5125 80 -1 30`
    - The arguments in order mean:
      - `5125`: This is the queue number we chose for activating the vtuber model.
      - `80`: This is the keycode for 'P', the keyboard shortcut that activates the vtuber model. You can find keycodes easily [here](https://www.toptal.com/developers/keycode).
      - `-1`: Because our keyboard shortcut is only one key, we set this argument to `-1` to indicate no second keypress.
      - `30`: This is the amount of time in seconds that we want the vtuber model to appear on screen. The queue will not process additional messages after this one until this time has elapsed.
    - Create a second sub-action. This one will disable the vtuber model after the 30 seconds have elapsed. The arguments are the same, but without the 30 second timeout.
      - `pythonw.exe shortcut_sender.py 5125 80 -1`
  - For the second action, activating an accessory, the arguments are similar, but the **queue** and **keycode** arguments will change.
    - Sub-action for enabling the accessory: `pythonw.exe shortcut_sender.py 5126 17 80 30`
    - This time, we use queue number `5126`, as this is the number we chose for activating the accessory.
    - The two keycodes are `17` and `80`, which correspond to 'Ctrl' and 'P' respectively.
    - `30` remains the same, supposing we want the accessory to last for 30 seconds.
    - Sub-action for disabling the accessory: `pythonw.exe shortcut_sender.py 5126 17 80`
- Streamerbot should now currently handle sending keyboard shortcuts for the vtuber and vtuber accessory even when pressing Ctrl/Shift/Alt during gameplay. 
 
## Notes
- The queue numbers are arbitrary, but be aware they are used as UDP ports, so if you're hosting any servers you might need to avoid overlapping ports. This will not be a concern for most people. 5125 is a decent enough number to start with, then just increment by one for each additional queue.
