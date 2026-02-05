from pynput import keyboard
import mido
import webview
import os
import json

outport = mido.open_output('fk2-midi', virtual=True)

# Load config
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

KEY_TO_NOTE = {pad['key']: pad['note'] for pad in config['pads']}
KEYS = [pad['key'] for pad in config['pads']]

window = None

class Api:
    def pad_press(self, index):
        if index < len(KEYS):
            key = KEYS[index]
            note = KEY_TO_NOTE.get(key)
            if note:
                msg = mido.Message('note_on', note=note, velocity=64, channel=0)
                outport.send(msg)
                print(f'Sent: {msg}')
                if window:
                    try:
                        window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padPress', {{detail: {index}}}))")
                    except:
                        pass
    
    def pad_release(self, index):
        if index < len(KEYS):
            key = KEYS[index]
            note = KEY_TO_NOTE.get(key)
            if note:
                msg = mido.Message('note_off', note=note, velocity=0, channel=0)
                outport.send(msg)
                print(f'Sent: {msg}')
                if window:
                    try:
                        window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padRelease', {{detail: {index}}}))")
                    except:
                        pass

def on_press(key):
    try:
        note = KEY_TO_NOTE.get(key.char)
        if note:
            msg = mido.Message('note_on', note=note, velocity=64, channel=0)
            outport.send(msg)
            print(f'Sent: {msg}')
            idx = KEYS.index(key.char)
            if window:
                try:
                    window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padPress', {{detail: {idx}}}))")
                except:
                    pass
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
                try:
                    window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padRelease', {{detail: {idx}}}))")
                except:
                    pass
    except (AttributeError, ValueError):
        pass

def main():
    global window
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    html_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'index.html'))
    print(f"Loading HTML from: {html_path}")
    window = webview.create_window('fk2-hid-midi', url=f'file://{html_path}', width=500, height=550, resizable=False, js_api=Api())
    webview.start()

if __name__ == "__main__":
    main()
