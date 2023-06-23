import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score

#importing data_________________________________

with open('roomData.json', 'r') as file:
    rawData=file.read()

obj = json.loads(rawData)

#methods________________________________________

def rowEmpty(room):
    for i in range(sensorCount):
        row.append(0)
    row.append(room)

def rowVerify():
    for i in row:
        if(i == 0):
            return False
    return True

#Processing settings____________________________

data = []
sensorCount = 5
timeInterval = 2

row = []
room = int(obj[0]["room"])
rowEmpty(room)

curentSecond = -30

#Processing into triplets_______________________
curentSecond = int(obj[0]["dataEntry"]["created_at"][-2:])
for entry in obj:
    entryTime = int(entry["dataEntry"]["created_at"][-2:])
    entryPwr = int(entry["dataEntry"]["pwr"])
    entrySensor = int(entry["dataEntry"]["sensor"]) - 1

    if(room != int(entry["room"])):
        room = int(entry["room"])
        curentSecond = entryTime
        row = []
        rowEmpty(room)

    if(entryTime <= (curentSecond + timeInterval - 1)):
        row[entrySensor] = entryPwr
    else:
        data.append(row)

        curentSecond = entryTime
        row = []
        rowEmpty(room)
        row[entrySensor] = entryPwr

#Training___________________________________________

coordinates = np.array([d[:-1] for d in data])
labels = np.array([d[-1] for d in data])


print(data)

X_train, X_test, y_train, y_test = train_test_split(coordinates, labels, test_size=0.2)

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_scaled, y_train)


y_pred = knn.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)


new_coordinates = [[20, 13, 5,0,0], [-70, -80, -40,0,0]]
new_coordinates_scaled = scaler.transform(new_coordinates)
new_predictions = knn.predict(new_coordinates_scaled)
print("Predictions for new coordinates:", new_predictions)

#changes in this file did show an improvement in the accuracy of the model
#the changes are setting the currentTime to the first value in the list. unconditional addition to the data list. time interval from 1 to 2 seconds