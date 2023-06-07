import json

with open('roomData.json', 'r') as file:
    rawData=file.read()

obj = json.loads(rawData)

# print(obj[0]["dataEntry"]["pwr"])

def rowEmpty():
    for i in range(sensorCount):
        row.append(0)

def rowVerify():
    for i in row:
        if(i == 0):
            return False
    return True



data = []
sensorCount = 3
timeInterval = 1


row = []
rowEmpty()

curentSecond = -1

for entry in obj:
    entryTime = int(entry["dataEntry"]["created_at"][-2:])
    entryPwr = int(entry["dataEntry"]["pwr"])
    entrySensor = int(entry["dataEntry"]["sensor"][-1]) - 1

    if(entryTime <= (curentSecond + timeInterval - 1)):
        row[entrySensor] = entryPwr
    elif(rowVerify()):
        data.append(row)
        curentSecond = entryTime
        row = []
        rowEmpty()
        row[entrySensor] = entryPwr
    else:
        curentSecond = entryTime
        row = []
        rowEmpty()
        row[entrySensor] = entryPwr

print(data)