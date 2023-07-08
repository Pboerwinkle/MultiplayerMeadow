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

class bee:
	def __init__(self, pos, connection, address):
		self.pos = pos
		self.inputs = []
		self.outputs = []
		self.connection = connection
		self.address = address
		print("Connected by "+str(self.address))
		self.disconnected = False
		clientWaiter = threading.Thread(target=self.waitOnClient)
		clientWaiter.start()

	def waitOnClient(self):
		with self.connection:
			while True:
				rawData = self.connection.recv(10240)
				decodedDatas = rawData.decode("utf-8")
				if(decodedDatas != "no controls"):
					datas = json.loads(decodedDatas)
					for data in datas:
						if not rawData or data["quit"]:
							print(self.address[0]+" disconnected")
							self.connection.sendall("ok".encode("utf-8"))
							self.disconnected = True
							break
						self.inputs.append(data)
#				else:
#					print("no input")
				if(self.disconnected):
					break
				if(self.outputs):
					msg = json.dumps(self.outputs)
					self.connection.sendall(msg.encode("utf-8"))
				else:
					self.connection.sendall("no frames".encode("utf-8"))
				self.outputs.clear()

	def doInputs(self):
		currentInputs = self.inputs.copy()
		for index, controlFrame in enumerate(currentInputs):
			if(controlFrame["left"]):
				self.pos[0] -= 1
			if(controlFrame["right"]):
				self.pos[0] += 1
			if(controlFrame["down"]):
				self.pos[1] += 1
			if(controlFrame["up"]):
				self.pos[1] -= 1
			self.inputs.pop(0)

def createClientHandlers():
	global clients
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("", 15000))
		s.listen()
		while True:
			connection, address = s.accept()
			clients.append(bee([random.randint(500, 550), random.randint(270, 320)], connection, address))

clients = []
clientHandlerCreater = threading.Thread(target=createClientHandlers)
clientHandlerCreater.start()

meadowImg = pygame.image.load("meadow.png")
beeImg = pygame.image.load("bee.png")

while True:
	clock.tick(framerate)
	disconnectedClients = []
	for index, client in enumerate(clients):
		client.doInputs()

		#print(len(client.outputs))
		if(len(client.outputs) <= 3):
			client.outputs.append([])
			lastOutput = len(client.outputs)-1
			client.outputs[lastOutput].append(["meadowImg", [0-client.pos[0], 0-client.pos[1]]])
			for otherClient in clients:
				client.outputs[lastOutput].append(["beeImg", [otherClient.pos[0]-client.pos[0], otherClient.pos[1]-client.pos[1]]])

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
