import operator
import re
list=[1,2,3,4,5]

print("valor ", list)		
for i in list:
	print("valuendo", i)
	list.pop(0)
print("valor ", list)