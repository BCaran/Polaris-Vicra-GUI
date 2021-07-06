from tkinter import *
from tkinter import scrolledtext
import serial
import time
import numpy as np
from tkinter import messagebox
import math


#Global variables
StartTrackingPressed = False
LoggingEnabled = False
LoggedData = np.array([0, 0, 0, 0, 0, 0, 0])

#Open serial communication
ser = serial.Serial(
    port='COM6',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
if ser.isOpen():
    ser.close()
ser.open()
ser.isOpen()

#Create window
window = Tk()

window.title("Polaris Vicra Tracking")

window.geometry('510x210')

#Polaris reset routine
def ndiRESET():
    ser.write("RESET 0\r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if buffer == "RESETBE6F":
                btn_ResetSystem.config(bg = "green")
                break
            else:
                btn_ResetSystem.config(bg = "red")
                break
        else:
            buffer += oneByte.decode("ascii")

#Polaris initialize routine
def ndiINIT():
    ser.write("INIT \r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if buffer == "OKAYA896":
                btn_InitSystem.config(bg = "green")
                break
            else:
                btn_InitSystem.config(bg = "red")
                break
        else:
            buffer += oneByte.decode("ascii")

#Commands for adding tool to handle
def ndiPHRQ(): #Assigns a port handle to a tooL
    ser.write("PHRQ *********1****\r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":   #method should returns bytes
            break
        else:
            buffer += oneByte.decode("ascii")

def ndiPHSR(): 
    ser.write("PHSR \r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":    #method should returns bytes
            break
        else:
            buffer += oneByte.decode("ascii")

def ndiPVWR():
    file =  open(toolName.get() + ".txt", 'r')
    countOK = 1
    while True:
        # Get next line from file
        line = file.readline()
        if not line:
            break
        ser.write(("PVWR " + line.strip() + "\r").encode())
        buffer = "" #1
        while (1):
            oneByte = ser.read(1)
            if oneByte == b"\r":
                if buffer == "OKAYA896":
                    if countOK == 12:
                        btn_addToolToHandle.config(bg = "green")
                        break
                    else:
                        countOK = countOK + 1
                        break
                else:
                    btn_addToolToHandle.config(bg = "red")
            else:
                buffer += oneByte.decode("ascii")
    file.close()
    return

def rememberStart():
    VicraOutput = ndiTX()
    StartPositionText.delete(0,'end')
    StartPositionText.insert(END, VicraOutput)

def rememberStop():
    VicraOutput = ndiTX()
    EndPositionText.delete(0,'end')
    EndPositionText.insert(END, VicraOutput)

def addToolToHandl():
    ndiPHRQ()
    ndiPHSR()
    ndiPVWR()

def ndiPINIT():
    ser.write("PINIT 01\r".encode())
    buffer = "" #12
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if(buffer == "OKAYA896"):
                btn_InitToolHandle.config(bg = "green")
                break
            else:
                btn_InitToolHandle.config(bg = "red")
        else:
            buffer += oneByte.decode("ascii")

def ndiPENA():
    ser.write("PENA 01D\r".encode())
    buffer = "" #12
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if buffer != "OKAYA896":
                btn_InitToolHandle.config(bg = "red")
            else:
                break
        else:
            buffer += oneByte.decode("ascii")

def initializePortHandle():
    ndiPINIT()
    ndiPENA()

def ndiTSTART():
    ser.write("TSTART \r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if(buffer == "OKAYA896"):
                btn_StartTracking.config(bg = "green")
                break
            else:
                btn_StartTracking.config(bg = "red")
        else:
            buffer += oneByte.decode("ascii")

def ndiTSTOP():
    ser.write("TSTOP \r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":
            if(buffer == "OKAYA896"):
                btn_StartTracking.config(bg = "SystemButtonFace")
                break
            else:
                btn_StopTracking.config(bg = "red")
        else:
            buffer += oneByte.decode("ascii")

def ndiTX():
    global a
    ser.write("TX 0001\r".encode())
    buffer = ""
    while (1):
        oneByte = ser.read(1)
        if oneByte == b"\r":    #method should returns bytes
            if buffer[4:11] == "MISSING":
                a = [-1, -1, -1, -1, -1, -1, -1]
                return a
            else:
                #a = [Qwo, Qx, Qy, Qz, Tx, Ty, Tz]
                a = [int(buffer[4:10])/10000, int(buffer[10:16])/10000, int(buffer[16:22])/10000, int(buffer[22:28])/10000, int(buffer[28:35])/100, int(buffer[35:42])/100, int(buffer[42:49])/100]
                return a
        else:
            buffer += oneByte.decode("ascii")

def StartTracking():
    global StartTrackingPressed
    global LoggingEnabled
    global LoggedData
    StartTrackingPressed = True

    if StartTrackingPressed == True:
        ndiTSTART()
    while(StartTrackingPressed == True):
        VicraOutput = ndiTX()
        if LoggingEnabled == True:
            newData = np.array(VicraOutput)
            LoggedData = np.vstack([LoggedData, newData])
        OutputLabel.config(text = VicraOutput)
        window.update()

def StopTracking():
    ndiTSTOP()
    global LoggingEnabled
    global StartTrackingPressed
    global LoggedData
    StartTrackingPressed = False
    if LoggingEnabled == True:
        btn_LogTracking.config(bg = "SystemButtonFace")
    LoggingEnabled = False
    window.update()

def StartLogging():
    global LoggingEnabled
    LoggingEnabled = True
    btn_LogTracking.config(bg = "green")

def SaveLog():
    global LoggedData
    global LoggingEnabled
    LoggingEnabled = False

    LoggedData = np.delete(LoggedData, 0, 0)
    np.savetxt(LogFileName.get() + ".csv", LoggedData, delimiter =', ', fmt='%f') 
    LoggedData = np.array([0, 0, 0, 0, 0, 0, 0])


#Button for system reset
btn_ResetSystem = Button(window, text="Reset System", command = ndiRESET)
btn_ResetSystem.grid(column=0, row=1)

#Button for system initialization
btn_InitSystem = Button(window, text="Initialize System", command = ndiINIT)
btn_InitSystem.grid(column=0, row=2)

#Entry for tool name
toolNameLabel = Label(window, text="Enter tool file name", font=("Arial", 10))
toolNameLabel.grid(column=0, row=3)
toolName = Entry(window,width=15)
toolName.insert(END, "MARKER1")
toolName.grid(column=0, row=4)

#Button for adding tool to handle
btn_addToolToHandle = Button(window, text = "Add tool to handle", command = addToolToHandl)
btn_addToolToHandle.grid(column=0, row=5)

#Button for handle initialization
btn_InitToolHandle = Button(window, text = "Initialize tool handle", command = initializePortHandle)
btn_InitToolHandle.grid(column=0, row=6)

#Space for printing current location
OutputNameLabel = Label(window, text = "Qo        Qx          Qy          Qz          Tx          Ty          Tz", font='Helvetica 9 bold')
OutputNameLabel.grid(column=1, row=1)
OutputLabel = Label(window, text = "-")
OutputLabel.grid(column=1, row=2)

#Space for printing start position
StartPositionLabel = Label(window, text = "Start position", font='Helvetica 9 bold')
StartPositionLabel.grid(column=1, row=3)
StartPositionText = Entry(window,width=43)
StartPositionText.grid(column=1, row=4)

#Space for printing end position
EndPositionLabel = Label(window, text = "End position", font='Helvetica 9 bold')
EndPositionLabel.grid(column=1, row=5)
EndPositionText = Entry(window, width=43)
EndPositionText.grid(column=1, row=6)

#Button to  remember start pos
btn_RememberStart = Button(window, text = "Save start", command = rememberStart)
btn_RememberStart.grid(column=1, row=7)

#Button to  remember end pos
btn_RememberEnd = Button(window, text = "Save stop", command = rememberStop)
btn_RememberEnd.grid(column=1, row=8)

#Button top start tracking
btn_StartTracking = Button(window, text = "Start tracking", command = StartTracking)
btn_StartTracking.grid(column=2, row=1)

#Button to stop tracking
btn_StopTracking = Button(window, text = "Stop tracking", command = StopTracking)
btn_StopTracking.grid(column=2, row=2)

#Button to log tracking
btn_LogTracking = Button(window, text = "Log tracking", command = StartLogging)
btn_LogTracking.grid(column=2, row=3)

#Entry for tool name
LogFileNameLabel = Label(window, text="Enter log file name", font=("Arial", 10))
LogFileNameLabel.grid(column=2, row=4)
LogFileName = Entry(window,width=15)
LogFileName.grid(column=2, row=5)
LogFileName.insert(END, "mjerenje")

#Button for saving logged file
btn_SaveLog = Button(window, text = "Save log", command = SaveLog)
btn_SaveLog.grid(column=2, row=6)



window.mainloop()



