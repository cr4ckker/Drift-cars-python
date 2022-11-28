import numpy as np
import tkinter as tk
import time, keyboard

from threading import Thread

from math import cos, acos, radians, degrees, sin, sqrt

from models import Car, Smoke

Objects = [Car(1, [500, 500], 30, 15, speed=5, color='#cc0000'), Car(2, [600, 500], 30, 15, speed=5, keys=['w','s','a','d'], color='#0000cc')]

drift_tails = {}

def hyp(vec):
    return sqrt(vec[0]**2 + vec[1]**2)

def Normalize(Vec):
    if Vec[0] == 0 and Vec[1] == 0:
        Vec[1] = 1
    Magnitude = sqrt(Vec[0]**2 + Vec[1]**2)
    Vec[0] /= Magnitude
    Vec[1] /= Magnitude
    return Vec

def GetLines(obj):
        return [[obj[i-1], obj[i]] for i in range(-1, len(obj)-1)]

def GetCenter(obj):
    return sum(map(lambda x: np.array(x), obj))/len(obj)

def CreateMove():
    drift_tail_num = {}
    direction = np.array([0.0, -1.0])
    while True:
        for obj in Objects:
            if obj.Type == 'car':
                obj.vector = Normalize(obj.vector*4*obj.velocity**2 + obj.direction)
                if keyboard.is_pressed('f5'):
                    obj.pos = np.array([500, 500], dtype='float64')
                    obj.x, obj.y = obj.pos
                # if keyboard.is_pressed(obj.keys[0]) and keyboard.is_pressed(obj.keys[1]): 
                #     obj.velocity *= 0.96
                else:
                    if keyboard.is_pressed(obj.keys[0]):
                        obj.velocity += (obj.speed - obj.velocity) * 0.01
                        gas = 1
                    if keyboard.is_pressed(obj.keys[1]):
                        obj.velocity += (-obj.speed/3 - obj.velocity) * 0.01
                        gas = 1
                if not keyboard.is_pressed(obj.keys[0]) and not keyboard.is_pressed(obj.keys[1]):
                    gas = 2
                if keyboard.is_pressed(obj.keys[2]):
                    obj.rotation -= min(2 * obj.velocity/obj.speed*1.5, 2)
                    obj.wheel_angle = max(-50 * (abs(obj.velocity)/obj.speed)*1.5, -50)
                if keyboard.is_pressed(obj.keys[3]):
                    obj.rotation += min(2 * obj.velocity/obj.speed*1.5, 2)
                    obj.wheel_angle = min(50 * (abs(obj.velocity)/obj.speed)*1.5, 50)
                if not keyboard.is_pressed(obj.keys[3]) and not keyboard.is_pressed(obj.keys[2]):
                    obj.wheel_angle *= 0.9

                if obj.velocity > 0.001 or obj.velocity < 0.001:
                    obj.direction = [direction[0] * cos(radians(obj.rotation)) - direction[1] * sin(radians(obj.rotation)), direction[0] * sin(radians(obj.rotation)) + direction[1] * cos(radians(obj.rotation))]
                    obj.velocity *= 0.995
                    obj.pos += obj.vector * obj.velocity
                    obj.x, obj.y = obj.pos

                    try:
                        obj.drift_angle = degrees(acos(np.array(obj.direction).dot(obj.vector) / ((hyp(obj.direction)*hyp(obj.vector)))))
                    except:
                        pass
                    if obj.drift_angle > 25:
                        drift_tail_num[obj.ID] += 1
                    else:
                        drift_tail_num[obj.ID] = 0

                    if drift_tail_num[obj.ID] % 4 == 0 and drift_tail_num[obj.ID] != 0:
                        if drift_tail_num[obj.ID] % (8*gas) == 0:
                            Objects.append(Smoke(obj.render[0], obj.vector*obj.velocity))
                            Objects.append(Smoke(obj.render[1], obj.vector*obj.velocity))
                        if obj.ID not in drift_tails:
                            drift_tails[obj.ID] = []
                        if drift_tail_num[obj.ID] > 4:
                            drift_tails[obj.ID][-1][0].append(obj.render[0])
                            drift_tails[obj.ID][-1][1].append(obj.render[1])
                            drift_tails[obj.ID][-1][2].append(obj.render[2])
                            drift_tails[obj.ID][-1][3].append(obj.render[3])
                        else:
                            drift_tails[obj.ID].append([[] for _ in range(4)])
                            drift_tails[obj.ID][-1][0].append(obj.render[0])
                            drift_tails[obj.ID][-1][1].append(obj.render[1])
                            drift_tails[obj.ID][-1][2].append(obj.render[2])
                            drift_tails[obj.ID][-1][3].append(obj.render[3])
        time.sleep(1/144)
        
def Render(canvas):
    for car in drift_tails:
        if len(drift_tails[car]) > 2:
            drift_tails[car].remove(drift_tails[car][0])
        for tails in drift_tails[car]:
            for tail in tails:
                if len(tail) > 1:
                    canvas.create_line(*tail, width=3, fill='#444444')

    for obj in Objects:
        obj.Render(canvas)
    
    

window = tk.Tk()
window.title('Drift car')
window.config(width=1500, height=900)
canvas = tk.Canvas(window, background='#cccccc', width=1500, height=900)
canvas.place(x=0, y=0)
Thread(target=CreateMove).start()
final_pos = 0
while True:
    window_xy = (window.winfo_rootx(), window.winfo_rooty())
    Render(canvas)
    window.update()
    canvas.delete(tk.ALL)
    time.sleep(1/144)
