import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
import requests


#importing local test data_________________________________

# with open('roomData.json', 'r') as file:
#     rawData=file.read()

# obj = json.loads(rawData)

#Processing settings____________________________
data = []
sensorCount = 1
timeInterval = 1

row = []
room = 0

curentSecond = -30

knn = 0
trained = False

#methods________________________________________

def rowEmpty(room):
    global row
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
    global data
    global row
    room = int(obj[0]["room"])
    rowEmpty(room)

    curentSecond = int(obj[0]["dataEntry"]["created_at"][-10:-8])
    for entry in obj:
        entryTime = int(entry["dataEntry"]["created_at"][-10:-8])
        entryPwr = int(entry["dataEntry"]["PWR"])
        entrySensor = int(entry["dataEntry"]["sensor"])

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
    print(data)
    coordinates = np.array([d[:-1] for d in data])
    labels = np.array([d[-1] for d in data])

    print(list(zip(coordinates, labels)))

    X_train, X_test, y_train, y_test = train_test_split(coordinates, labels, test_size=0.1)

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
            row[t["sensor"]] = t["PWR"]
        else:
            result.append(row)
            
            currentMac = t["MAC"]
            for i in range(sensorCount):
                row.append(0)
            row.append(currentMac)

            row[t["sensor"]] = t["PWR"]
    
    return result

#receiving request_________________________________________

ndata = []
training_url = "http://192.168.56.1:8000/api/roomdata/details"
getPrediction_url = "http://192.168.56.1:8000/api/dataentry/prediction"
sendPrediction_url = "http://192.168.56.1:8000/api/device/updateRoom"

def training_request():
    try:
        response = requests.get(training_url)

        if response.status_code == 200:
            print('Training request successful')
            ndata = response.json()
            pross(ndata)
        else:
            print('Request failed')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)




def prediction_request():
    if(trained):
        try:
            response = requests.get(getPrediction_url)

            if response.status_code == 200:
                print('Prediction request successful')
                toPredict = response.json()
                print(toPredict)

                cordsAndMac = prepare(toPredict)

                new_cordinates = np.array([c[:-1] for c in cordsAndMac])
                new_MAC = np.array([c[-1] for c in cordsAndMac])
                predictions = predict(data, new_cordinates)

                MacAndPrediction = [[x, y] for x, y in zip(new_MAC, predictions)]

                try:
                    response = requests.post(sendPrediction_url, data=MacAndPrediction, headers = {'Content-Type': 'application/json'})

                    if response.status_code == 200:
                        print('Training request successful')
                        ndata = response.json()
                    else:
                        print('Request failed')
                        print('Status Code:', response.status_code)
                        print('Response:', response.text)

                except requests.exceptions.RequestException as e:
                    print('An error occurred:', e)
            else:
                print('Request failed')
                print('Status Code:', response.status_code)
                print('Response:', response.text)

        except requests.exceptions.RequestException as e:
            print('An error occurred:', e)
    else:
        print("no models yet")

while True:
    print("1 - Ask for data to train a model\n2 - Get and send back prediction")
    choice = input()
    if(choice == "1"):
        training_request()
    elif(choice == "2"):
        prediction_request()
    else:
        break