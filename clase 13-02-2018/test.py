class ABa:
	def __init__(self, algo):
		print(algo)
	def sampleFunc(self, arg):
		print('you called sampleFunc({})'.format(arg))

globals()['A'+"ba".title()]('esto')
