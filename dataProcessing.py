import json
import numpy as np
from sklearn.linear_model import LinearRegression

with open('roomData.json', 'r') as file:
    rawData=file.read()

obj = json.loads(rawData)

# print(obj[0]["dataEntry"]["pwr"])

def rowEmpty(room):
    for i in range(sensorCount):
        row.append(0)
    row.append(room)

def rowVerify():
    for i in row:
        if(i == 0):
            return False
    return True



data = []
sensorCount = 3
timeInterval = 1


row = []
rowEmpty(int(obj[0]["room"]))

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
        rowEmpty(int(entry["room"]))
        row[entrySensor] = entryPwr
    else:
        curentSecond = entryTime
        row = []
        rowEmpty(int(entry["room"]))
        row[entrySensor] = entryPwr

print(data)

X_train = np.array([d[:-1] for d in data])
y_train = np.array([d[-1] for d in data])

print(X_train)
print(y_train)
model = LinearRegression()
model.fit(X_train, y_train)

new_entry = [50, 40, 50]

predicted_value = model.predict([new_entry])

print("Predicted value: ", predicted_value[0])