import win32api
import win32con
import win32gui
import tkinter as tk
import numpy as np
import ultralytics
import threading
import math
import time 
import cv2
import mss
import random
import winsound


class Config:
    def __init__(self):
        
        
        self.width = 1920
        self.height = 1080
        
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        self.capture_width = 120
        self.capture_height = 170
        self.capture_left = self.center_x - self.capture_width // 2
        self.capture_top = self.center_y - self.capture_height // 2
        self.crosshairX = self.capture_width // 2
        self.crosshairY = self.capture_height // 2
        
        self.region = {"top": self.capture_top,"left": self.capture_left,"width": self.capture_width,"height": self.capture_height+100}

        self.Running = True
        self.AimToggle = True
        self.delay = 0.07
        self.radius = 10

config = Config()


def CreateOverlay():

    root = tk.Tk()
    root.title("Manuroger's cpu muncher")
    root.geometry('250x650')
    tk.Label(root, text="opula trigger dessist (2)", font=("Helvetica", 14)).pack()
    
    def quitProgram():
        
        config.AimToggle = False
        config.Running = False
        root.quit()

    def DelayConfigurator(Delay):
        config.delay = float(Delay)

    def ManualCenterConfiguratorX(ValueX):
        config.crosshairX =  config.capture_width // 2 + int(ValueX)
        config.center_x = config.width // 2 + int(ValueX)
        overlay.geometry(f'150x150+{str(config.center_x - config.radius)}+{str(config.center_y - config.radius)}')

    def ManualCenterConfiguratorY(ValueY):
        config.crosshairY = config.capture_height // 2 + int(ValueY)
        config.center_y = config.height // 2 + int(ValueY)
        overlay.geometry(f'150x150+{str(config.center_x - config.radius)}+{str(config.center_y - config.radius)}')
        
    def CreateSlider(root, LabelText, fromV, toV, resolution, command, setValue):
        tk.Label(root, text=LabelText).pack()
        Slider = tk.Scale(root, from_=fromV, to=toV, resolution=resolution, orient=tk.HORIZONTAL, command = command)
        Slider.pack()
        Slider.set(setValue)

    #Manual Center Offset Sliders
    CreateSlider(root, "Offset CenterX Manually", -100, 100, 1, ManualCenterConfiguratorX, 0)
    CreateSlider(root, "Offset CenterY Manually", -100, 100, 1, ManualCenterConfiguratorY, 0)

    #Delay Slider
    CreateSlider(root, "Delay after shot", 0.003, 1.5, 0.001, DelayConfigurator, config.delay)
    
    #Quit Button
    QuitButton = tk.Button(root, text="Quit", command=quitProgram)
    QuitButton.pack()

    #Ingame Overlay
    overlay = tk.Toplevel(root)
    overlay.geometry(f'150x150+{str(config.center_x - config.radius)}+{str(config.center_y - config.radius)}')
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', 'blue')
    #Canvas
    canvas = tk.Canvas(overlay, width=150, height=150, bg='blue', bd=0, highlightthickness=0)
    canvas.pack()
    config.fovC = canvas.create_oval(0, 0, config.radius*2, config.radius*2, outline='green')

    overlay.mainloop()
    
def main():
    
    x1=y1=x2=y2=0
    moveX = 0
    moveY = 0
    displacementX= -1
    displacementY= -1
    noDetectionIteration = 1
    
    #model = ultralytics.YOLO("Fortnite by hogthewog.onnx", task = 'detect')
    model = ultralytics.YOLO("yolov8n.pt")
    screenCapture = mss.mss()
    
    overlayThread = threading.Thread(target=CreateOverlay)
    overlayThread.start()
    
    while config.Running:
        time.sleep(0.001)

        if win32api.GetAsyncKeyState(0x05) & 1: #KEY TO STOP TRIGGERBOT
                config.AimToggle = not config.AimToggle
                if config.AimToggle == False:
                    winsound.Beep(500, 50)
                else:
                    winsound.Beep(1000, 50)
                time.sleep(1)
            
        if config.AimToggle == False:
            continue
        
        GameFrame = np.array(screenCapture.grab(config.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2BGR)
        results = model.predict(source = GameFrame, conf = 0.45, classes=[0], verbose=False, max_det = 10)     
        boxes = results[0].boxes.xyxy

        if len(boxes) > 0:
            x1, y1, x2, y2 = boxes[0].tolist()

            displacementX = x2-x1
            displacementY = y2-y1
            
            moveX = int((displacementX // 2 + x1 - config.crosshairX))
            moveY = int((displacementY //2 + y1 - config.crosshairY))

            noDetectionIteration = 0

        if abs(moveX) <= displacementX//2 and abs(moveY) <= displacementY//2 and noDetectionIteration  <= 3:
            
            noDetectionIteration += 1
            
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.04)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(config.delay)
            
    overlayThread.join()
                 
if __name__ == "__main__":
    main()







    #FOR DEBUGGING             
        #cv2.rectangle(GameFrame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
        #cv2.imshow("Game Frame", GameFrame)        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
            #config.Running = False
            #break       
    #cv2.destroyAllWindows()
