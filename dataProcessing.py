import json

with open('roomData.json', 'r') as file:
    rawData=file.read()

obj = json.loads(rawData)

# print(obj[0]["dataEntry"]["pwr"])

def sensorFilter(value):
    
    pwr = value["pwr"]
    

data = []
row = [0, 0, 0]

timeInterval = 1
rowIndex = 1
isRowValid = True
curentSecond = -1

for entry in obj:
    entryTime = int(entry["dataEntry"]["created_at"][-2:])
    entryPwr = int(entry["dataEntry"]["pwr"])
    entrySensor = int(entry["dataEntry"]["sensor"][-1]) - 1

    if(entryTime == curentSecond):
        row[entrySensor] = entryPwr
    elif(row[0]!=0 and row[1]!=0 and row[2]!=0 and entryTime > (curentSecond + timeInterval - 1)):
        data.append(row)
        isRowValid = True
    else:
        curentSecond = entryTime
        row = [0, 0, 0]
        row[entrySensor] = entryPwr
        isRowValid = False

print(data)