import socket
import threading
import json
import time
import pygame
pygame.init()

ipAddress = input("ip address: ")
port = int(input("port: "))
controls = []
closedCommunication = False

keyBinds = {"left": [97, 1073741904],
			"right": [100, 1073741903],
			"down": [115, 1073741905], 
			"up": [119, 1073741906]}
keysPressed = {"left": False,
			   "right": False,
			   "down": False,
			   "up": False,
			   "quit": False}

meadowImg = pygame.image.load("meadow.png")
beeImg = pygame.image.load("bee.png")
zoomFactor = 2

imgs = {"meadowImg": pygame.transform.scale_by(meadowImg, zoomFactor), "beeImg": pygame.transform.scale_by(beeImg, zoomFactor)}
frames = []

screenWidth = 600
screenHeight = 600
screenSize = (screenWidth,screenHeight)
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("client view","client view")
clock = pygame.time.Clock()
framerate = 60

def commWithServer(ipAddress, port):
	global closedCommunication
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((ipAddress, port))
		while True:
			if(controls):
				msg = json.dumps(controls)
				s.sendall(msg.encode("utf-8"))
			else:
				s.sendall("no controls".encode("utf-8"))
			for control in controls:
				if(control["quit"]):
					closedCommunication = True
					return
			controls.clear()
			rawData = s.recv(1024)
			data = json.loads(rawData.decode("utf-8"))
			frames.append(data)
serverConnection = threading.Thread(target=commWithServer, args=(ipAddress, port,))
serverConnection.start()

while True:
	#print(len(controls))
	clock.tick(framerate)
	if(closedCommunication):
		print("closed")
		pygame.quit()
		quit()
	events = pygame.event.get()
	for event in events:
		if(event.type == pygame.QUIT):
			keysPressed["quit"] = True
		if(event.type == pygame.KEYDOWN):
			for key in keyBinds:
				for bind in keyBinds[key]:
					if(event.key == bind):
						keysPressed[key] = True
		if(event.type == pygame.KEYUP):
			for key in keyBinds:
				for bind in keyBinds[key]:
					if(event.key == bind):
						keysPressed[key] = False
	if(len(controls) <= 3):
		controls.append(keysPressed.copy())
	for frame in frames:
		screen.fill((0, 0, 0))
		for img in frame:
			screen.blit(imgs[img[0]], (img[1][0]*zoomFactor+round(screenSize[0]/2), img[1][1]*zoomFactor+round(screenSize[0]/2)))
		pygame.display.flip()
		frames.pop(0)
