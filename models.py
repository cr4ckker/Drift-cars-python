import numpy as np
import random

from math import cos, sin, radians

class Car:
    def __init__(self, pos, length, width, rotation=0, speed=5) -> None:
        self.x, self.y = pos
        self.pos = np.array(pos, dtype='float64')

        self.length = length
        self.width = width

        points = [
                [0, 0],
                [self.width, 0], 
                [self.width, self.length], 
                [0, self.length]
                ]

        self.rotation = rotation

        self.speed = speed
        self.vector = np.array([0.0, 0.0])
        self.direction = np.array([0.0, -1.0])
        self.velocity = 0.0

        self.map = points
        self.render = list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))
        self.lines = self.GetLines(self.render)
    
    def Render(self, canvas):
        render = self.GetMap()
        center = self.GetCenter(render)
        back = self.GetBackAxis(render)
        self.render = list(map(lambda line: [(back[0] - line[0]) * cos(radians(self.rotation)) - (back[1] - line[1]) * sin(radians(self.rotation)) + center[0], (back[0] - line[0]) * sin(radians(self.rotation)) + (back[1] - line[1]) * cos(radians(self.rotation)) + center[1]], render))
        canvas.create_polygon(*self.render, fill='#ff0000')

    def GetLines(self, obj):
        return [[obj[i-1], obj[i]] for i in range(-1, len(obj)-1)]
    
    def GetCenter(self, obj):
        return sum(map(lambda x: np.array(x), obj))/len(obj)
    
    def GetBackAxis(self, obj):
        return self.GetCenter(obj) - [0, self.length/2]
    
    def GetMap(self):
        return list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))
    
class Smoke:
    def __init__(self, pos, vector=[0,0]) -> None:
        self.size = random.randint(5, 11)
        self.pos = np.array(pos)
        self.vector = np.array(vector)
        self.rotation = random.randint(-45, 45)
        self.rotation_velocity = random.randint(-5, 5)
        self.size_transform_velocity = random.randint(1, 2)
        self.color = 102
        self.alive = True

    def Render(self, canvas):
        if self.alive:
            self.size += self.size_transform_velocity / 2
            self.pos += self.vector*0.6
            self.x, self.y = self.pos
            self.rotation += self.rotation_velocity
            self.color += 3
            self.map = [
                    [0, 0],
                    [self.size, 0],
                    [self.size, self.size],
                    [0, self.size]
                    ]
            render = self.GetMap()
            center = self.GetCenter(render)
            self.render = list(map(lambda line: [(center[0] - line[0]) * cos(radians(self.rotation)) - (center[1] - line[1]) * sin(radians(self.rotation)) + center[0], (center[0] - line[0]) * sin(radians(self.rotation)) + (center[1] - line[1]) * cos(radians(self.rotation)) + center[1]], render))
            canvas.create_polygon(*self.render, fill=f'#{hex(self.color).split("0x")[1] * 3}')
            if hex(self.color) == '0xcc':
                self.alive = False
    
    def GetCenter(self, obj):
        return sum(map(lambda x: np.array(x), obj))/len(obj)

    def GetMap(self):
        return list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))
    
