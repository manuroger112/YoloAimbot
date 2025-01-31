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
        self.InstaStep = False
        self.RectangleB = True
        self.IndividualMovementDelay = None
        self.Sensitivity = 1
        self.MovementCoefficientX = 0.80
        self.MovementCoefficientY = 0.65
        self.movementSteps = 5
        self.delay = 0.007
        self.radius = 60
        self.rectC = None
        self.fovC = None


config = Config()


def CreateOverlay():

    root = tk.Tk()
    root.title("Manuroger's cpu muncher")
    root.geometry('250x650')
    tk.Label(root, text="opula aim dessist", font=("Helvetica", 14)).pack()
    
    def quitProgram():
        
        config.AimToggle = False
        config.Running = False
        root.quit()

    def SensitivityConfigurator(Sens):
        config.Sensitivity = float(Sens)

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

    def CoefficientXConfigurator(ValueX):
        config.MovementCoefficientX = float(ValueX)

    def CoefficientYConfigurator(ValueY):
        config.MovementCoefficientY = float(ValueY)

    def RadiusConfigurator(Radius):
        config.radius = int(Radius)
        canvas.delete(config.fovC)
        overlay.geometry(f'150x150+{str(config.center_x - config.radius)}+{str(config.center_y - config.radius)}')
        config.fovC = canvas.create_oval(0, 0, config.radius*2, config.radius*2, outline='green')
        
    def InstaStepButton():
        config.InstaStep = not config.InstaStep
        if config.InstaStep == True:
            config.movementSteps = 1
            InstaStepLabel.config(text=f"1 movement is currently done in {config.movementSteps} steps")
        else:
            config.movementSteps = 5
            InstaStepLabel.config(text=f"1 movement is currently done in {config.movementSteps} steps")

    def AimButton():
        config.AimToggle = not config.AimToggle
        AimLabel.config(text=f"Aimbot in currently set to: {config.AimToggle}")

    def ShowHideRect():
        config.RectangleB = not config.RectangleB
        if config.RectangleB == False:
            canvas.delete(config.rectC)
        else:
            config.rectC = canvas.create_rectangle(config.radius-10, config.radius-10, config.radius +10, config.radius+10,outline = "black")
            
    def CreateSlider(root, LabelText, fromV, toV, resolution, command, setValue):
        tk.Label(root, text=LabelText).pack()
        Slider = tk.Scale(root, from_=fromV, to=toV, resolution=resolution, orient=tk.HORIZONTAL, command = command)
        Slider.pack()
        Slider.set(setValue)

    #Manual Center Offset Sliders
    CreateSlider(root, "Offset CenterX Manually", -100, 100, 1, ManualCenterConfiguratorX, 0)
    CreateSlider(root, "Offset CenterY Manually", -100, 100, 1, ManualCenterConfiguratorY, 0)
    #Sensitivity Slider
    CreateSlider(root, "Ingame Sensitivity", 0.1, 10, 0.01, SensitivityConfigurator, config.Sensitivity)
    #Delay Slider
    CreateSlider(root, "Delay after movement", 0.003, 0.05, 0.001, DelayConfigurator, config.delay)
    #Movement Coefficients
    CreateSlider(root, "Movement Scalar CoefficientX", 0.5, 5, 0.01, CoefficientXConfigurator, config.MovementCoefficientX)
    CreateSlider(root, "Movement Scalar CoefficientY", 0.5, 5, 0.01, CoefficientYConfigurator, config.MovementCoefficientY)
    #Aim Radius
    CreateSlider(root, "Fov", 10, config.capture_width//2, 1, RadiusConfigurator, config.radius)
    
    #Toggle Insta Step
    InstaStepLabel = tk.Label(root, text=f"1 movement is currently done in {config.movementSteps} steps")
    InstaStepLabel.pack()
    togInstaStep = tk.Button(root, text= "Toggle Insta Step", command=InstaStepButton)
    togInstaStep.pack()
    
    #Toggle AimBot
    AimLabel = tk.Label(root, text=f"Aimbot in currently set to: {config.AimToggle}")
    AimLabel.pack()
    AimToggler = tk.Button(root, text= "Toggle Aim", command=AimButton)
    AimToggler.pack()
    
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
    config.rectC = canvas.create_rectangle(config.radius-10, config.radius-10, config.radius +10, config.radius+10,outline = "black")

    tk.Button(root, text="Show/Hide Rectangle", command=ShowHideRect).pack()
    
    overlay.mainloop()
    
def main():
    
    indexMin = 0
    
    x1=y1=x2=y2=0

    #model = ultralytics.YOLO("Fortnite by hogthewog.onnx", task = 'detect')
    model = ultralytics.YOLO("yolov8n.pt")
    screenCapture = mss.mss()
    
    overlayThread = threading.Thread(target=CreateOverlay)
    overlayThread.start()
    
    while config.Running:
        time.sleep(0.001)

        if config.AimToggle == False:
                time.sleep(1)
                continue
        
        GameFrame = np.array(screenCapture.grab(config.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2BGR)
        results = model.predict(source = GameFrame, conf = 0.5, classes=[0], verbose=False, max_det = 10)     
        boxes = results[0].boxes.xyxy

        distsm = 99999
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes[0].tolist()
            moveX = int(((x2 - x1) // 2+x1 - config.crosshairX))
            moveY = int((y1+(y2 - y1) * 0.085 - config.crosshairY))
            distance = math.sqrt(math.pow(moveX, 2) + math.pow(moveY, 2))
            if distsm > distance:
                distsm = distance
                indexMin = i

         
        if len(boxes) > 0:
            x1, y1, x2, y2 = boxes[indexMin].tolist()
            moveX = int(((x2 - x1) // 2+x1 - config.crosshairX) // config.Sensitivity)
            moveY = int((y1+(y2 - y1) * 0.085 - config.crosshairY) // config.Sensitivity)
            distance = math.sqrt(math.pow(moveX, 2) + math.pow(moveY, 2))
            if distance < config.radius:
                for i in range(config.movementSteps):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(moveX*config.MovementCoefficientX), int(moveY*config.MovementCoefficientY) , 0, 0)
                    time.sleep(config.delay)
                    
       #FOR DEBUGGING             
            #cv2.rectangle(GameFrame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
        #cv2.imshow("Game Frame", GameFrame)        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
            #config.Running = False
            #break       
    cv2.destroyAllWindows()
    overlayThread.join()
                 
if __name__ == "__main__":
    main()
