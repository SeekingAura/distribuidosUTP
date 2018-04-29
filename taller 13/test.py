cadena="test.txt"
cadena="test v1.txt"
dicto={"value.txt":"1", "value v1.txt": "2", "value v2.txt":"3", "otro.txt":"4", "otro v1.txt":"5"}



temp=""
temporal=""
pos=0
version=0
for i in dicto:
	if("value" in i):
		temp=""
		temporal=""
		pos=0
		extension=False
		#print("esta en value")
		for enum, j in enumerate(reversed(i)):
			if j.isdigit():
				temp=j+temp
			elif(not extension):
				if(j=="."):
					extension=True
					print("YOLO")
				elif(j=="v" and len(temp)>0):
					pos=enum
					break
				elif(len(temp)>0):
					temp=""
					pos=enum
					break
			else:
				if(j=="v"):
					pos=enum
					print("ACA ->", i[-(enum+2)])
					break
				else:
					temp=""
					pos=enum
					break
		if(len(temp)>0):
			
			print("estado ->", i[:-(pos+2)])
			print("a ", i[-(pos+2)])
			version=int(temp)
			print("version ->", temp)
		
