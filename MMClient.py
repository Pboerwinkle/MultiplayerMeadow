import random
import socket
import threading
import json
import time
import pygame
pygame.init()

ipAddress = input("ip address: ")
port = input("port(default: 15000): ")
if port == "":
	port = 15000
else:
	port = int(port)
closedCommunication = False

keyBinds = {"left": [97, 1073741904],
			"right": [100, 1073741903],
			"down": [115, 1073741905], 
			"up": [119, 1073741906]}
keysPressed = {"left": False,
			   "right": False,
			   "down": False,
			   "up": False}

meadowImg = pygame.image.load("meadow.png")
beeImg = pygame.image.load("bee.png")
zoomFactor = 2

imgs = {"meadowImg": pygame.transform.scale2x(meadowImg), "beeImg": pygame.transform.scale2x(beeImg)}

screenWidth = 600
screenHeight = 600
screenSize = (screenWidth,screenHeight)
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("client view","client view")
clock = pygame.time.Clock()
framerate = 30

player = {"pos": [random.randint(500, 550), random.randint(270, 320)], "quit": False}
frames = []

def commWServer(ipAddress, port):
	def toServer():
		global player
		nonlocal toServerClosed
		nonlocal s
		while True:
			clock.tick(15)
			msg = json.dumps(player)
			s.sendall(msg.encode("utf-8"))
			if(player["quit"]):
				toServerClosed = True
				return
	def fromServer():
		global closedCommunication
		global frames
		global player
		nonlocal fromServerClosed
		nonlocal s
		while True:
			clock.tick(15)
			if(player["quit"]):
				response = ""
				print("waiting for response...")
				while response != "ok":
					response = s.recv(1024).decode("utf-8")
				print("...got response")
				closedCommunication = True
				fromServerClosed = True
				return
			rawData = s.recv(1024)
			decodedDatas = rawData.decode("utf-8")
			if decodedDatas:
				datas = json.loads(decodedDatas)
				frames.append(datas)
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((ipAddress, port))
		toServerClosed = False
		fromServerClosed = False

		toServerThrd = threading.Thread(target=toServer, args=())
		toServerThrd.start()
		fromServerThrd = threading.Thread(target=fromServer, args=())
		fromServerThrd.start()
		while not toServerClosed and not fromServerClosed:
			time.sleep(15)

commWServerThrd = threading.Thread(target=commWServer, args=(ipAddress, port,))
commWServerThrd.start()

while True:
	clock.tick(framerate)
	if(closedCommunication):
		print("closed")
		pygame.quit()
		quit()
	events = pygame.event.get()
	for event in events:
		if(event.type == pygame.QUIT):
			player["quit"] = True
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

	if keysPressed["left"]:
		player["pos"][0] -= 3
	if keysPressed["right"]:
		player["pos"][0] += 3
	if keysPressed["up"]:
		player["pos"][1] -= 3
	if keysPressed["down"]:
		player["pos"][1] += 3

	for frame in frames:
		screen.fill((0, 0, 0))
		for img in frame:
			screen.blit(imgs[img[0]], ((img[1][0]-player["pos"][0])*zoomFactor+round(screenSize[0]/2), (img[1][1]-player["pos"][1])*zoomFactor+round(screenSize[0]/2)))
		screen.blit(imgs["beeImg"], (round(screenWidth/2), round(screenHeight/2)))
		pygame.display.flip()
	frames.clear()
