import numpy as np
import tkinter as tk
import keyboard
import time, win32api, platform
from pygame.time import Clock

from threading import Thread

from math import cos, acos, radians, degrees, sin, sqrt

from models import Car, Smoke, NonCollideTypes
from funcs import hyp, rotate, GetCenter, GetLines

Objects = [Car(1, [500, 500], 30, 15, speed=5, color='#cc0000'), Car(2, [600, 600], 30, 15, speed=5, keys=['w','s','a','d', 'space'], color='#0000cc')]

drift_tails = {}

def init():
    global SCREEN_REFRESH_RATE
    if platform.system() == 'Windows':
        device = win32api.EnumDisplayDevices()
        SCREEN_REFRESH_RATE = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
    else:
        SCREEN_REFRESH_RATE = 144
    rotate(0, *[1 for _ in range(6)])

def CreateMove():
    global CreateMove_limiter
    CreateMove_limiter = Clock()
    drift_tail_num = {}
    while True:
        for obj in Objects:
            if obj.Type == 'car':
                obj.CreateMove(Objects)
                if obj.velocity > 0.001 or obj.velocity < -0.001:
                    try:
                        obj.drift_angle = degrees(acos(np.array(obj.direction).dot(obj.vector) / ((hyp(obj.direction)*hyp(obj.vector)))))
                    except:
                        pass
                    if obj.drift_angle > 25:
                        drift_tail_num[obj.ID] += 1
                    else:
                        drift_tail_num[obj.ID] = 0

                    if drift_tail_num[obj.ID] % 8 == 0 and drift_tail_num[obj.ID] != 0 or drift_tail_num[obj.ID] == 1:
                        if drift_tail_num[obj.ID] % 8 == 0:
                            Objects.append(Smoke(obj.render[0] + obj.vector * obj.velocity, obj.vector*obj.velocity))
                            Objects.append(Smoke(obj.render[1] + obj.vector * obj.velocity, obj.vector*obj.velocity))
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
            elif obj.Type == 'bullet':
                if not obj.alive:
                    Objects.remove(obj)
                    continue
                obj.CreateMove()
                for second_object in Objects.copy():
                    if obj.Collide(second_object):
                        break
        CreateMove_limiter.tick(144)
        
def ParticleMove():
    global ParticleMove_limiter
    ParticleMove_limiter = Clock()
    while True:
        for obj in Objects.copy():
            if obj.Type == 'smoke':
                if not obj.alive:
                    Objects.remove(obj)
                    continue
                obj.CreateMove()
        ParticleMove_limiter.tick(60)

def Render(canvas):
    canvas.create_text(50, 15, font=('Arial', 14), text=f'FPS: {int(Render_limiter.get_fps())}')
    canvas.create_text(50, 35, font=('Arial', 14), text=f'TPS: {int(CreateMove_limiter.get_fps())}')
    canvas.create_text(50, 55, font=('Arial', 14), text=f'PTPS: {int(ParticleMove_limiter.get_fps())}')
    _drift_tails = drift_tails.copy()
    for car in _drift_tails:
        if len(_drift_tails[car]) > 2:
            _drift_tails[car].remove(_drift_tails[car][0])
        for tails in _drift_tails[car]:
            for tail in tails:
                if len(tail) > 1:
                    canvas.create_line(*tail, width=3, fill='#444444')
    for obj in Objects.copy():
        obj.Render(canvas)


init()
Render_limiter = Clock()
window = tk.Tk()
window.title('Drift car')
window.config(width=1500, height=800)
canvas = tk.Canvas(window, background='#cccccc', width=1500, height=800)
canvas.place(x=0, y=0)
Thread(target=CreateMove).start()
Thread(target=ParticleMove).start()
final_pos = 0
while True:
    window_xy = (window.winfo_rootx(), window.winfo_rooty())
    Render(canvas)
    window.update()
    canvas.delete(tk.ALL)
    Render_limiter.tick(SCREEN_REFRESH_RATE)
