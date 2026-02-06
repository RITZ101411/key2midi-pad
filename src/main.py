from pynput import keyboard
import mido
import webview
import os
import json
import time

# Load config
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

KEY_TO_NOTE = {pad['key']: pad['note'] for pad in config['pads']}
KEYS = [pad['key'] for pad in config['pads']]

window = None
outport = None
listener = None
window_focused = False

# タイミング記録用
key_timings = {}

def calc_velocity(key_down_time, previous_key_down_time, previous_key_up_time):
    # 押下速度（前回KeyUpからの時間差）
    dt_press = key_down_time - previous_key_up_time
    dt_press = max(50, min(dt_press, 300))  # clamp 50〜300ms（範囲を広げる）
    p = 1.0 - (dt_press - 50) / (300 - 50)

    # 連打間隔（前回KeyDownからの時間差）
    dt_repeat = key_down_time - previous_key_down_time
    dt_repeat = max(100, min(dt_repeat, 500))  # clamp 100〜500ms（範囲を広げる）
    r = 1.0 - (dt_repeat - 100) / (500 - 100)

    # ハイブリッド合成（押下速度重視）
    energy = 0.7 * p + 0.3 * r

    # Velocityに変換（60〜110）範囲を狭める
    velocity = int(60 + energy * 50)
    return velocity

class Api:
    def set_window_focus(self, focused):
        global window_focused
        window_focused = focused
        print(f'Window focus: {focused}')
        return True
    
    def set_always_on_top(self, on_top):
        if window:
            window.on_top = on_top
            print(f'Always on top: {on_top}')
        return True
    
    def pad_press(self, index):
        if index < len(KEYS):
            key = KEYS[index]
            note = KEY_TO_NOTE.get(key)
            if note:
                current_time = time.time() * 1000  # ms
                
                if key not in key_timings:
                    key_timings[key] = {'down': 0, 'up': 0}
                
                prev_down = key_timings[key]['down']
                prev_up = key_timings[key]['up']
                
                if prev_down == 0:
                    velocity = 64
                else:
                    velocity = calc_velocity(current_time, prev_down, prev_up)
                
                key_timings[key]['down'] = current_time
                
                msg = mido.Message('note_on', note=note, velocity=velocity, channel=0)
                outport.send(msg)
                print(f'Sent: {msg}')
                if window:
                    try:
                        window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padPress', {{detail: {{index: {index}, velocity: {velocity}}}}}))")
                    except:
                        pass
    
    def pad_release(self, index):
        if index < len(KEYS):
            key = KEYS[index]
            note = KEY_TO_NOTE.get(key)
            if note:
                current_time = time.time() * 1000  # ms
                key_timings[key]['up'] = current_time
                
                msg = mido.Message('note_off', note=note, velocity=0, channel=0)
                outport.send(msg)
                print(f'Sent: {msg}')
                if window:
                    try:
                        window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padRelease', {{detail: {{index: {index}}}}}))")
                    except:
                        pass

def on_press(key):
    if not window_focused:
        return
    try:
        note = KEY_TO_NOTE.get(key.char)
        if note:
            current_time = time.time() * 1000  # ms
            
            if key.char not in key_timings:
                key_timings[key.char] = {'down': 0, 'up': 0}
            
            prev_down = key_timings[key.char]['down']
            prev_up = key_timings[key.char]['up']
            
            if prev_down == 0:
                velocity = 64
            else:
                velocity = calc_velocity(current_time, prev_down, prev_up)
            
            key_timings[key.char]['down'] = current_time
            
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=0)
            outport.send(msg)
            print(f'Sent: {msg}')
            idx = KEYS.index(key.char)
            if window:
                try:
                    window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padPress', {{detail: {{index: {idx}, velocity: {velocity}}}}}))")
                except:
                    pass
    except (AttributeError, ValueError):
        pass

def on_release(key):
    if not window_focused:
        return
    try:
        note = KEY_TO_NOTE.get(key.char)
        if note:
            current_time = time.time() * 1000  # ms
            key_timings[key.char]['up'] = current_time
            
            msg = mido.Message('note_off', note=note, velocity=0, channel=0)
            outport.send(msg)
            print(f'Sent: {msg}')
            idx = KEYS.index(key.char)
            if window:
                try:
                    window.evaluate_js(f"window.dispatchEvent(new CustomEvent('padRelease', {{detail: {{index: {idx}}}}}))")
                except:
                    pass
    except (AttributeError, ValueError):
        pass

def main():
    global window, outport
    
    # デフォルトデバイスを開く
    try:
        outport = mido.open_output('fk2-midi', virtual=True)
        print(f'Default MIDI device: fk2-midi (virtual)')
    except:
        outputs = mido.get_output_names()
        if outputs:
            outport = mido.open_output(outputs[0])
            print(f'Default MIDI device: {outputs[0]}')
        else:
            print('No MIDI devices available')
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    html_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'index.html'))
    print(f"Loading HTML from: {html_path}")
    window = webview.create_window('fk2-hid-midi', url=f'file://{html_path}', width=500, height=600, resizable=False, js_api=Api())
    webview.start()

if __name__ == "__main__":
    main()
