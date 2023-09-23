import socket
import json
import threading
import time
import random
import pygame
pygame.init()

screenWidth = 1200
screenHeight = 600
screen_size = (screenWidth,screenHeight)
screen = pygame.display.set_mode(screen_size)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("server view","server view")
clock = pygame.time.Clock()
framerate = 60

def getMapState(address):
	mapState = []
	mapState.append(["meadowImg", [0, 0]])
	for client in clients:
		if client.address != address:
			mapState.append(["beeImg", [client.pos[0], client.pos[1]]])
	return mapState


class bee:
	def __init__(self, pos, connection, address):
		self.pos = pos
		self.connection = connection
		self.address = address
		self.inputs = []
		print("Connected by "+str(self.address))
		self.disconnected = False
		toClientThrd = threading.Thread(target=self.toClient)
		toClientThrd.start()
		fromClientThrd = threading.Thread(target=self.fromClient)
		fromClientThrd.start()

	def toClient(self):
		while True:
			clock.tick(15)
			if(self.disconnected):
				break
			msg = json.dumps(getMapState(self.address))
			self.connection.sendall(msg.encode("utf-8"))
	def fromClient(self):
		while True:
			clock.tick(15)
			rawData = self.connection.recv(10240)
			decodedDatas = rawData.decode("utf-8")
			if decodedDatas:
				datas = json.loads(decodedDatas)
				if datas["quit"]:
					print(self.address[0]+" disconnected")
					self.connection.sendall("ok".encode("utf-8"))
					self.disconnected = True
					break
				self.pos = datas["pos"]

def createClientHandlers():
	global clients
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("", 15000))
		s.listen()
		while True:
			connection, address = s.accept()
			clients.append(bee([0, 0], connection, address))

clients = []
clientHandlerCreater = threading.Thread(target=createClientHandlers)
clientHandlerCreater.start()

meadowImg = pygame.image.load("meadow.png")
beeImg = pygame.image.load("bee.png")

while True:
	clock.tick(framerate)
	disconnectedClients = []
	for index, client in enumerate(clients):
		if(client.disconnected):
			disconnectedClients.append(index)

	disconnectedClients.sort(reverse=True)
	for client in disconnectedClients:
		clients.pop(client)

	screen.fill([0, 0, 0])
	screen.blit(meadowImg, (0, 0))
	for client in clients:
		screen.blit(beeImg, client.pos)
	pygame.display.flip()
