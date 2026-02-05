from pynput import keyboard
import mido
import webview
import os

outport = mido.open_output('fk2-midi', virtual=True)

KEY_TO_NOTE = {
    'a': 60, 's': 62, 'd': 64, 'f': 65, 
    'g': 67, 'h': 69, 'j': 71, 'k': 72,
    'w': 61, 'e': 63, 't': 66, 'y': 68, 
    'u': 70, 'i': 72, 'o': 74, 'p': 76
}

KEYS = ['w', 'e', 't', 'y', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'u', 'i', 'o', 'p']

window = None

def on_press(key):
    try:
        note = KEY_TO_NOTE.get(key.char)
        if note:
            msg = mido.Message('note_on', note=note, velocity=64, channel=0)
            outport.send(msg)
            print(f'Sent: {msg}')
            idx = KEYS.index(key.char)
            if window:
                window.evaluate_js(f"document.getElementById('pad{idx}').classList.add('active')")
    except (AttributeError, ValueError):
        pass

def on_release(key):
    try:
        note = KEY_TO_NOTE.get(key.char)
        if note:
            msg = mido.Message('note_off', note=note, velocity=0, channel=0)
            outport.send(msg)
            print(f'Sent: {msg}')
            idx = KEYS.index(key.char)
            if window:
                window.evaluate_js(f"document.getElementById('pad{idx}').classList.remove('active')")
    except (AttributeError, ValueError):
        pass

def main():
    global window
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'index.html')
    window = webview.create_window('fk2-hid-midi', url=html_path, width=590, height=700, resizable=False)
    webview.start()

if __name__ == "__main__":
    main()
