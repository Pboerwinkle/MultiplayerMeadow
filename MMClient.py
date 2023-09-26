import sys
import random
import socket
import threading
import json
import time
import copy
import pygame
pygame.init()

if len(sys.argv) == 1:
	ipAddress = "127.0.0.1"
	port = 15000
elif len(sys.argv) > 3:
	print("only two arguments are supported:\npython3 MMServer.py IPADDRESS(default: 127.0.0.1) PORT(default: 15000)")
	python.quit()
	quit()
elif len(sys.argv) == 2:
	if "." in sys.argv[1]:
		ipAddress = sys.argv[1]
		port = 15000
	else:
		ipAddress = "127.0.0.1"
		port = int(sys.argv[1])
else:
	ipAddress = sys.argv[1]
	port = int(sys.argv[2])

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

imgs = {"meadowImg": pygame.transform.scale(meadowImg, (2400, 1200)), "beeImg": pygame.transform.scale(beeImg, (38, 40))}

screenWidth = 600
screenHeight = 600
screenSize = (screenWidth,screenHeight)
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("client view","client view")
clock = pygame.time.Clock()
framerate = 60

player = {"pos": [random.randint(500, 550), random.randint(270, 320)], "quit": False}
frames = []
prevFrame = []

def commWServer(ipAddress, port):
	global closedCommunication
	def toServer():
		global player
		nonlocal toServerClosed
		nonlocal s
		quitted = False
		while True:
			clock.tick(30)
			if player["quit"]:
				quitted = True
			msg = json.dumps(player)+";"
			s.sendall(msg.encode("utf-8"))
			if quitted:
				toServerClosed = True
				return
	def fromServer():
		global frames
		global player
		nonlocal fromServerClosed
		nonlocal s
		decodedDatas = ""
		while True:
			clock.tick(30)
			rawData = s.recv(1024)
			decodedDatas += rawData.decode("utf-8")
			if decodedDatas:
				while ";" in decodedDatas:
					index = decodedDatas.index(";")
					shortData = decodedDatas[:index]
					if shortData == "quit":
						fromServerClosed = True
						return
					datas = json.loads(shortData)
					decodedDatas = decodedDatas[index+1:]
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
			time.sleep(2)
		closedCommunication = True

commWServerThrd = threading.Thread(target=commWServer, args=(ipAddress, port,))
commWServerThrd.start()

def blitImg(img, pos):
	x = (pos[0]-player["pos"][0]) * zoomFactor + round(screenSize[0]/2)
	y = (pos[1]-player["pos"][1]) * zoomFactor + round(screenSize[1]/2)
	screen.blit(img, (x, y))
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
			screen.fill((0, 0, 0))
			pygame.display.flip()
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
		player["pos"][0] -= 2
	if keysPressed["right"]:
		player["pos"][0] += 2
	if keysPressed["up"]:
		player["pos"][1] -= 2
	if keysPressed["down"]:
		player["pos"][1] += 2

	if not player["quit"]:
		if frames:
			for frame in frames:
				screen.fill((0, 0, 0))
				blitImg(imgs["meadowImg"], (0, 0))

				for img in frame:
					blitImg(imgs[img[0]], (img[1][0], img[1][1]))

				blitImg(imgs["beeImg"], (player["pos"][0], player["pos"][1]))
				pygame.display.flip()
			prevFrame = copy.deepcopy(frames[-1])
			frames.clear()
		else:
			screen.fill((0, 0, 0))
			blitImg(imgs["meadowImg"], (0, 0))

			for img in prevFrame:
				blitImg(imgs[img[0]], (img[1][0], img[1][1]))

			blitImg(imgs["beeImg"], (player["pos"][0], player["pos"][1]))
			pygame.display.flip()
