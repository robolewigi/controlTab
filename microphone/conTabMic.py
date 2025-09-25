import vosk,queue,json,os,time,psutil
import threading
import numpy as np
import sounddevice as sd
from collections import deque
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller, Key, Listener
from word2number import w2n

keyboard = Controller()
mouse = MouseController()
click = [Button.left, Button.right, Button.middle]

class Variables:
 modelPath = "vosk-model-en-us-0.22-lgraph"
 model = None
 used = False
 # Voice toggle
 keys = [False, False,False]  # 0=access, 1=toggleVoice 2-holdForDebug
 modi = False
 toggleWord = "listen"
 showText = True
 charKeys = ['b','t','f'] #0-holdToAccess 1-toggleToAccess 2-holdForDebug
 modiKeys = [Key.ctrl, Key.shift, Key.alt, Key.cmd]
 selectedModi = 0
 voiceCommands = [
  ["the", ["0;"]],
  ["control said", ["1;z;0"]],
  ["move mouse !n right !n down", ["2;!n;!n"]],
  ["left mouse button", ["4;0"]],
  ["semi colon", ["0;!!"]],
  ["main menu", ["3;0;9999", "4;0"]],
  ["times !n then", ["5;!n"]]]
 sounds = [
  "/usr/share/sounds/sound-icons/pisk-up.wav",
  "/usr/share/sounds/sound-icons/pisk-down.wav"]
v = Variables()

q = queue.Queue()
sound_queue = queue.Queue()
command_queue = queue.Queue()

def play_sound(index):
 path = v.sounds[index]
 os.system(f"aplay {path} >/dev/null 2>&1")
 if index==0: print("active")
 else: print("deactive")

def convertNumber(s):
 try:
  s = s.strip().lower()
  if s.startswith(("negative ", "minus ")):
   return -w2n.word_to_num(s.split(" ", 1)[1])
  return w2n.word_to_num(s)
 except:
  return None

def convertVoice(text):
 if ";" not in text: text=f"0;{text}" 
 segs = text.split(";")
 print(segs)
 cmd = int(segs[0])
 arg1 = segs[1] if len(segs) > 1 else ""
 arg2 = segs[2] if len(segs) > 2 else None
 if cmd == 0:
  keyboard.type(arg1.replace("!!", ";"))
  keyboard.tap(Key.space)
 elif cmd == 1 and arg2 is not None:
  keyboard.press(v.modiKeys[int(arg2)])
  keyboard.type(arg1.replace("!!", ";"))
  keyboard.release(v.modiKeys[int(arg2)])
 elif cmd == 2:
  mouse.move(int(arg1), int(arg2))
 elif cmd == 3:
  mouse.position = (int(arg1), int(arg2))
 elif cmd == 4:
  mouse.click(click[int(arg1)], 1)

def makeNumber(i, text):
 nums = []
 idx = -1
 script = v.voiceCommands[i][0].split()
 for idx, token in enumerate(script):
  if token== "!n" and 0< idx< len(script)- 1:
   before, after= script[idx- 1], script[idx+ 1]
   segment= text.split(before, 1)[-1].split(after, 1)[0]
   num= convertNumber(segment.strip())
   nums.append(num if num is not None else 0)
 return nums

def textConvert(text):
 parts= text.split()
 for i, (cmd, actions) in enumerate(v.voiceCommands):
  words = cmd.split()
  if words[0] in parts and words[-1] in parts:

   f = " ".join(actions)
   if "!n" in f:
    nums = makeNumber(i, text)
    for n in nums:
     if isinstance(n,int):
      f = f.replace("!n", str(n), 1)
     else: f= f.replace("!n", str(0),1)
    if f.startswith("5;"):
     loopWord= None
     idx= parts.index(words[0])
     if idx>0:
      loopWord=str(parts[idx-1])
      startReplace= text.find(loopWord)
      combinedWord=""
      for k in range(int(f[2:])):
       combinedWord=combinedWord+ loopWord
      text= text[:startReplace]+combinedWord+text[startReplace+len(loopWord):] 
     f=""          
   try:
    start = text.find(words[0])
    end = text.find(words[-1],start) + len(words[-1])
   except: start,end=0,len(text)-1
   text = text[:start] + f + text[end:]
 for word in text.split():
  command_queue.put(word)

def audio_callback(indata, frames, time_info, status):
 if status: print(status)
 q.put(bytes(indata))

def recLoop():
 print("recognitionOn")
 rec = vosk.KaldiRecognizer(v.model, 16000)
 with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16', channels=1, callback=audio_callback):
  while v.used:
   try: data = q.get(timeout=0.05)
   except queue.Empty: continue
   if rec.AcceptWaveform(data):
    result = rec.Result()
    text = json.loads(result).get("text", "")
    if not text: continue
    if v.showText and text:
     print("showText:", text)

    if v.toggleWord and text.startswith(v.toggleWord):
     v.keys[1] = not v.keys[1]
     play_sound(0 if v.keys[1] else 1)
     text = text[len(v.toggleWord):]
    if not (v.keys[0] or v.keys[1]): continue
    textConvert(text)

def onPress(key):
 if key == v.modiKeys[v.selectedModi]:
  v.modi = True
 if hasattr(key, 'char') and key.char == v.charKeys[1] and v.modi:
  v.keys[1] = not v.keys[1]
  play_sound(0 if v.keys[1] else 1)
 elif hasattr(key, 'char') and key.char == v.charKeys[0] and v.modi:
  v.keys[0] = True
 elif hasattr(key, 'char') and key.char == v.charKeys[2] and v.modi:
  v.keys[2] = True

def onRelease(key):
 if key == v.modiKeys[v.selectedModi]:
  v.modi = False
 if hasattr(key, 'char') and key.char == v.charKeys[0]:
  v.keys[0] = False
 if hasattr(key, 'char') and key.char == v.charKeys[2]:
  v.keys[2] = False

def execLoop():
 while v.used:
  try: word = command_queue.get(timeout=0.1)
  except queue.Empty: continue
  convertVoice(word)
  command_queue.task_done()

def printUsage():
 proc = psutil.Process(os.getpid())
 print("Memory:", proc.memory_info().rss // 1024000, "MB","totalCpu:", f"{proc.cpu_percent(interval=0.1)/os.cpu_count():.1f}", "%")

def helpCommand():
 return f"""
Model: {v.modelPath}
ShowText: {v.showText}
activateKey: {v.charKeys[0]} + {v.modiKeys[v.selectedModi]}/ToggleKey: {v.charKeys[1]} + {v.modiKeys[v.selectedModi]}/debug: {v.charKeys[2]}
VoiceCommands: {[vc[0] for vc in v.voiceCommands]}
toggleWord: {v.toggleWord}

"""

def saveFunc():
 save = f"""{{
  "vosk": {json.dumps(v.modelPath)},
  "showText": {json.dumps(v.showText)},
  "characterKey": {json.dumps(v.charKeys)},
  "toggleWord": {json.dumps(v.toggleWord)},
  "#V modifiers:0-ctrl 1-shift 2-alt 3-cmd V": null,
  "modifierKey": {json.dumps(v.selectedModi)},
  "#V 0;string 1;string;ctrlShiftAltCmd 2(mouse);x;y 3(set);x;y 4;lmbRmbMmb 5;loopTimesLeft V": null,
  "commands": {json.dumps(v.voiceCommands)},
  "onOffSounds": {json.dumps(v.sounds)}
 }}"""
 with open("save.json", "w") as f:
    f.write(save)
def loadSave():
 if not os.path.exists("save.json") or os.stat("save.json").st_size == 0:
  saveFunc()
 try:
  with open("save.json", "r") as f:
   save = json.load(f)
   v.modelPath=save["vosk"]
   v.showText=save["showText"]
   v.charKeys=save["characterKey"]
   v.selectedModi=save["modifierKey"]
   v.voiceCommands=save["commands"]
   v.sounds=save["onOffSounds"]
   v.toggleWord=save["toggleWord"]
   v.used=False
 except FileNotFoundError:
  saveFunc()
  if not v.used:
   v.used=True
   loadSave()

loadSave()
vosk.SetLogLevel(-1)
try: v.model = vosk.Model(v.modelPath)
except:
 path = input("Vosk model not found. Enter path: ").strip()
 v.model = vosk.Model(path)

print(helpCommand())
v.used = True
threading.Thread(target=recLoop, daemon=True).start()
threading.Thread(target=execLoop, daemon=True).start()
listener = Listener(on_press=onPress, on_release=onRelease).start()
while True:
 time.sleep(0.5)
 if v.keys[2]: printUsage()
