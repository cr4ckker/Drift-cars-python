import numpy as np
import numba
import random, keyboard, time

from math import cos, sin, radians
from funcs import Normalize, rotate, hyp

direction = np.array([0.0, 1.0])
NonCollideTypes = ['smoke', 'wheel']

class Car:
    Type = 'car'
    def __init__(self, ID, pos, length, width, rotation=0, speed=5, keys=['up', 'down', 'left', 'right', 'enter'], color='#cc0000') -> None:
        self.ID = ID
        self.lastshot_time = 0
        self.keys = keys
        self.color = color
        self.x, self.y = pos
        self.pos = np.array(pos, dtype='float64')

        self.length = length
        self.width = width

        self.wheels = [
            Wheel(np.array([-self.width/2, self.length/2-5]), True),
            Wheel(np.array([self.width/2, self.length/2-5]), True),
            Wheel(np.array([-self.width/2, -self.length/2+5]), False),
            Wheel(np.array([self.width/2, -self.length/2+5]), False)
        ]

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
        self.wheel_angle = 0.0
        self.drift_angle = 0.0

        self.map = points
        self.render = list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))
        self.lines = self.GetLines(self.render)
    
    def CreateMove(self, objects):
        self.vector = Normalize(self.vector*4*self.velocity**2 + self.direction)
        if keyboard.is_pressed('f5'):
            self.pos = np.array([500, 500], dtype='float64')
            self.x, self.y = self.pos

        if keyboard.is_pressed(self.keys[0]):
            self.velocity += (self.speed - self.velocity) * 0.01
        if keyboard.is_pressed(self.keys[1]):
            self.velocity += (-self.speed/3 - self.velocity) * 0.01
        if keyboard.is_pressed(self.keys[2]):
            self.rotation -= min(2 * self.velocity/self.speed*1.5, 2)
            self.wheel_angle = max(-50 * (abs(self.velocity)/self.speed)*1.5, -50)
        if keyboard.is_pressed(self.keys[3]):
            self.rotation += min(2 * self.velocity/self.speed*1.5, 2)
            self.wheel_angle = min(50 * (abs(self.velocity)/self.speed)*1.5, 50)

        if not keyboard.is_pressed(self.keys[3]) and not keyboard.is_pressed(self.keys[2]):
            self.wheel_angle *= 0.9

        if keyboard.is_pressed(self.keys[4]):
            if time.time() - self.lastshot_time > 1:
                self.lastshot_time = time.time()
                objects.append(Bullet(self.ID, self.GetCenter(self.render), self.direction))
        
        if self.velocity > 0.001 or self.velocity < -0.001:
            self.direction = rotate(self.rotation, *direction, *[0,0,0,0])
            self.velocity *= 0.995
            self.pos += self.vector * self.velocity
            self.x, self.y = self.pos

    def Render(self, canvas):
        for wheel in self.wheels:
            wheel.Render(canvas, self.GetCenter(self.GetMap()), [min(self.wheel_angle, 45.0), self.rotation], self.drift_angle)
        render = self.GetMap()
        center = self.GetCenter(render)
        back = self.GetBackAxis(render)
        self.render = [rotate(self.rotation, *point, *center, *back) for point in render]
        canvas.create_polygon(*self.render, fill=self.color)

    def GetLines(self, obj):
        return [[obj[i-1], obj[i]] for i in range(-1, len(obj)-1)]
    
    def GetCenter(self, obj):
        return sum(map(lambda x: np.array(x), obj))/len(obj)
    
    def GetBackAxis(self, obj):
        return self.GetCenter(obj) - [0, self.length/2]

    def GetMap(self):
        return list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))

    
class Smoke:
    Type = 'smoke'
    def __init__(self, pos, vector=[0,0]) -> None:
        self.size = random.randint(3, 10)
        self.pos = np.array(pos)
        self.vector = np.array(vector)
        self.rotation = random.randint(-45, 45)
        self.rotation_velocity = random.randint(-5, 5)
        self.size_transform_velocity = random.randint(1, 2)
        self.color_change_velocity = random.randint(3,5)
        self.color = 102
        self.alive = True
        self.map = [
                [0, 0],
                [self.size, 0],
                [self.size, self.size],
                [0, self.size]
                ]
        self.render = self.GetMap()

    def Render(self, canvas):
        if self.alive:
            canvas.create_polygon(*self.render, fill=f'#{hex(self.color).split("0x")[1] * 3}')

    def CreateMove(self):
        self.size += self.size_transform_velocity / 2
        self.pos += self.vector*0.6
        self.x, self.y = self.pos
        self.rotation += self.rotation_velocity
        self.color += self.color_change_velocity
        self.map = [
                [0, 0],
                [self.size, 0],
                [self.size, self.size],
                [0, self.size]
                ]
        render = self.GetMap()
        center = self.GetCenter(render)
        self.render = [rotate(self.rotation, *point, *center, *center) for point in render]
        if self.color > 204:
            self.alive = False
    
    def GetCenter(self, obj):
        return sum(map(lambda x: np.array(x), obj))/len(obj)

    def GetMap(self):
        return list(map(lambda point: [self.pos[0] + point[0], self.pos[1] + point[1]], self.map))


class Wheel:
    Type = 'wheel'
    def __init__(self, offset, rotating=False) -> None:
        self.offset = offset
        self.rotating = rotating
        self.height = 8
        self.width = 4
        self.map = [
                    [0, 0],
                    [self.width, 0],
                    [self.width, self.height],
                    [0, self.height]
                    ]

    def Render(self, canvas, pos, rotation, drift_angle):
        self.x, self.y = self.pos = self.x, self.y = self.pos = pos + self.offset - [self.width/2, -self.height*1.4]
        self.rotation = rotation
        center = pos
        render = self.GetMap()
        self.render = [rotate(self.rotation[1], *point, *center, *center) for point in render]
        if self.rotating:
            mp = cos(radians(min(drift_angle, 50)/25*90))
            self.rotation[0] *= mp
            center = self.GetCenter(self.render)
            self.render = [rotate(self.rotation[0], *point, *center, *center) for point in self.render]
        canvas.create_polygon(*self.render, fill='#111111')

    def GetCenter(self, obj):
        return sum(map(lambda x: np.array(x), obj))/len(obj)

    def GetMap(self):
        return list(map(lambda point: [self.x + point[0], self.y + point[1]], self.map))

class Bullet:
    Type = 'bullet'
    def __init__(self, ID, pos, vector, speed=5, radius=5) -> None:
        self.ID = ID
        self.pos = np.array(pos)
        self.vector = np.array(vector)
        self.speed = speed
        self.radius = radius
        self.alive = True
    
    def CreateMove(self):
        self.pos += self.vector * self.speed
        if self.pos[0] > 1500 or self.pos[0] < 0 or self.pos[1] < 0 or self.pos[1] > 800:
            self.alive = False
            print('dead')
    
    def Collide(self, obj):
        if obj.Type in NonCollideTypes:
            return False
        if obj.ID == self.ID:
            return False
        if obj.Type == 'car':
            obj: Car
            ranges = {}
            for line in obj.GetLines(obj.render):
                A, B = line

                d = np.array(A) - np.array(self.pos)
                n = np.array(Normalize([A[0]-B[0], A[1]-B[1]]))
                res = d - (d.dot(n))*n
                xx_yy = [(A[0], B[0]),(A[1], B[1])]
                final_x, final_y = self.pos[0]+res[0], self.pos[1]+res[1]

                if min(xx_yy[0]) >= final_x:
                    final_x = min(xx_yy[0])
                elif max(xx_yy[0]) <= final_x:
                    final_x = max(xx_yy[0])

                if min(xx_yy[1]) >= final_y:
                    final_y = min(xx_yy[1])
                elif max(xx_yy[1]) <= final_y:
                    final_y = max(xx_yy[1])

                ranges[str(np.math.sqrt((final_x - self.pos[0])**2 + (final_y - self.pos[1])**2))] = [final_x - self.pos[0], final_y - self.pos[1]]
            closest = min(map(lambda x: float(x), ranges.keys()))
            if closest < self.radius:
                self.alive = False
                obj.velocity = 0.0
                obj.vector = np.array([0.0, 0.0])
                return True

        elif obj.Type == 'bullet':
            if sum((obj.pos - self.pos)**2) < obj.radius**2 + self.radius**2 and self.ID != obj.ID:
                self.alive = False
                obj.alive = False
                return True
        return False
    
    def Render(self, canvas):
        canvas.create_oval(*self.pos, *self.pos, width=self.radius, fill='#0000cc')

