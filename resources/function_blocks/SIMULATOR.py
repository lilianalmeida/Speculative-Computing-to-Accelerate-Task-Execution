import numpy as np
import paho.mqtt.client as mqtt
import random
import numpy as np

# river
from river import neighbors
from river import metrics
from river import preprocessing

# scikit-learn
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

class SIMULATORInputGen:
    def paramsGeneration(self, event, var_index, event_table, speculable_variables, lookup_table):
        random_existing_input = random.choice(list(event_table))
        prev_var = eval(random_existing_input[var_index])
        
        # get random number between 0 and the penultimate index of the lookup table
        swap_index = random.randint(0, len(prev_var)-2)
        
        prev_var[swap_index], prev_var[swap_index+1] = prev_var[swap_index +1], prev_var[swap_index]
        
        return str(prev_var)

class SIMULATORSpeculators:
    def __init__ (self):
        self.streaming_model = None
        self.streaming_MAE = None
        self.batch_model = None
        self.batch_MAE = None
        
    def runStreamingRegressor(self, op, inputs, outputs, event_table):
        # parses inputs and outputs
        if inputs:
            input = list(inputs)[2]
            input = eval(input)
            input = [ item for elem in input for item in list(elem)]
            input = {k: v for k, v in enumerate(input)}
        if outputs:
            output = outputs[2]
            
        if op == "PREDICT":
            if self.streaming_model:
                # verifies if metric value is good enough for the value to be used
                if self.streaming_MAE.get() < 60:
                    return [self.streaming_model.predict_one(input)], self.streaming_MAE.get()
                
        elif op == "TRAIN_STREAM":
            if not self.streaming_model:
                self.streaming_model = neighbors.KNNRegressor(n_neighbors=3)
                self.streaming_MAE = metrics.MAE()
            
            # trains model         
            y_pred = self.streaming_model.predict_one(input)
            self.streaming_model = self.streaming_model.learn_one(input, output)
            self.streaming_MAE.update(output, y_pred)
            
        else: # TRAIN_BATCH
            return None
        
        return None

    # def runBatchRegressor(self, event, var_index, event_table, speculable_variables, lookup_table):
    def runBatchRegressor(self, op, inputs, outputs, event_table):            

        if op == "PREDICT":
            # parses inputs
            input = list(inputs)[2]
            input = eval(input)
            input = [ item for elem in input for item in list(elem)]
            input = [input]
            
            if self.batch_model:
                # verifies if metric value is good enough for the value to be used
                if self.batch_MAE < 60:
                    y_pred = self.batch_model.predict(input)
                    return y_pred, self.batch_MAE
                
                
        elif op == "TRAIN_BATCH":
            if len(event_table) < 20:
                return None
            
            # gets inputs and outputs
            inputs = []
            outputs = []

            for k,v in event_table.items():
                input = list(k)[2]
                input = eval(input)
                input = [ item for elem in input for item in list(elem)]
                inputs.append(input)

                output = v[2]
                outputs.append(output)
                
            # splits dataset and trains model
            X_train, X_test, y_train, y_test = train_test_split(inputs, outputs, test_size=0.25, random_state=1)
            new_batch_model = KNeighborsRegressor(n_neighbors=3)
            new_batch_model.fit(X_train, y_train)

            # predicts and evaluates
            y_pred = new_batch_model.predict(X_test)
            new_batch_MAE = mean_absolute_error(y_test, y_pred)
            
            # updates class variables
            self.batch_model = new_batch_model
            self.batch_MAE = new_batch_MAE
                        
            
        else: # TRAIN_STREAM
            return None
        
        return None
        

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

class Fitness:
    def __init__(self, route):
        self.route = route
        print("route: " , route)
        self.distance = 0
        self.fitness = 0.0

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness


class SIMULATOR:

    def schedule(self, event_name, event_value, params):

        if event_name == 'INIT':
            self.counter = 1
            return [None, None, None]

        elif event_name == 'RUN':
            # Should wait for the handler
            self.params = eval(params)
            
            print("Iteration: " , self.counter)
            self.counter += 1

            cityList = []
            for i in range(0, len(self.params)):
                cityList.append(City(self.params[i][0], self.params[i][1]))

            return [None, event_value, Fitness(cityList).routeDistance()]
