import time
import json 

c = 1

with open('logsreset.json', 'r') as file:
	data = json.load(file)

def error(dic):
	with open('logsreset.json', 'w') as file:
		json.dump(dic, file)

def loop():
	with open("data.json", "r") as file:
		dictData = json.load(file)

	for el in list(dictData.keys()):
		dictData[el]["images"] = 0
		dictData[el]["message"] = 0

	with open("data.json", "w") as file:
		json.dump(dictData, file)

if __name__ == "__main__":
	while True:
		try:
			loop()
			print("ЛИМИТ сброшен")
			time.sleep(86400)
			data[str(c)] = 'reset'
			error(data)
		except Exception as err:
			data[str(c)] = str(err)
			c += 1
			error(data)
