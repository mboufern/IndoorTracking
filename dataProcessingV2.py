import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from flask import Flask, request

#importing local test data_________________________________

# with open('roomData.json', 'r') as file:
#     rawData=file.read()

# obj = json.loads(rawData)

#Processing settings____________________________
data = []
sensorCount = 3
timeInterval = 1

row = []
room = 0

curentSecond = -30

knn = 0
trained = False

#methods________________________________________

def rowEmpty(room):
    for i in range(sensorCount):
        row.append(0)
    row.append(room)

def rowVerify(row):
    for i in row:
        if(i == 0):
            return False
    return True

#Processing into triplets and training_______________________

def pross(obj):
    room = int(obj[0]["room"])
    rowEmpty(room)
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
            if(rowVerify(row)):
                data.append(row)

            curentSecond = entryTime
            row = []
            rowEmpty(room)
            row[entrySensor] = entryPwr
    
        coordinates = np.array([d[:-1] for d in data])
        labels = np.array([d[-1] for d in data])

        print(coordinates)

        X_train, X_test, y_train, y_test = train_test_split(coordinates, labels, test_size=0.2, random_state=1)

        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(X_train_scaled, y_train)
        y_pred = knn.predict(X_test_scaled)

        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", accuracy)
        
        trained = True

#Prediction___________________________________________
def predict(data, new_coordinates):
    scaler = MinMaxScaler()
    # new_coordinates = [[20, 13, 5], [-70, -80, -40]]
    new_coordinates_scaled = scaler.transform(new_coordinates)
    new_predictions = knn.predict(new_coordinates_scaled)
    print("Predictions for new coordinates:", new_predictions)
    return new_predictions

#format the data to predict________________________________

def prepare(toPredict):
    result = []
    row = []
    currentMac = toPredict[0]["MAC"]
    
    for i in range(sensorCount):
        row.append(0)
    row.append(currentMac)

    for t in toPredict:
        if(t["MAC"] == currentMac):
            row[t["sensor"] - 1] = t["PWR"]
        else:
            if(rowVerify(row)):
                result.append(row)
            
            currentMac = t["MAC"]
            for i in range(sensorCount):
                row.append(0)
            row.append(currentMac)

            row[t["sensor"] - 1] = t["PWR"]
    
    return result

#receiving request_________________________________________

app = Flask(__name__)
ndata = []

@app.route('/trainModel', methods=['POST'])
def handle_request():
    # Access the request data
    ndata = request.get_json()
    pross(ndata)

    return 'data Processed'

@app.route('/predict', methods=['POST'])
def handle_another_request():
    if(trained):
        toPredict = request.get_json()
        cordsAndMac = prepare(toPredict)

        new_cordinates = np.array([c[:-1] for c in cordsAndMac])
        new_MAC = np.array([c[-1] for c in cordsAndMac])
        predictions = predict(data, new_cordinates)

        MacAndPrediction = [[x, y] for x, y in zip(new_MAC, new_cordinates)]
        return MacAndPrediction

if __name__ == '__main__':
    app.run()