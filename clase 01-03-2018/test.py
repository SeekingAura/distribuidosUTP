import threading
import time
class test:
	def __init__(self, id):
		self.id=id
		print("creado")
	
	def runServer(self):
		print("iniciado")
		for i in range(10):
			time.sleep(2)
			print("iterando ", i, self.id)
			self.change("hizo run")

	def runOther(self):
		print("iniciado")
		for i in range(25):
			time.sleep(1)
			print("otro ", i, self.id)
			self.change("hizo other")

	def change(self, value):
		self.id=value

#threadLock = threading.Lock()
if __name__ == '__main__':
	x={}
	print("algo" in [*x])