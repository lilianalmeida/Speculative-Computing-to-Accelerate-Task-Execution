import numpy as np
import time
import paho.mqtt.client as mqtt
import random

class CityInputGen:
    def params_generation(self, event, event_table, speculable_variables, lookup_table):
        prev_input = list(next(iter(event_table)))
        print("prev Input ", prev_input)
        
        # get random number between 0 and the penultimate index of the lookup table
        swap_index = random.randint(0, len(prev_input)-2)
        print("index ", swap_index)
        
        prev_input[swap_index], prev_input[swap_index+1] = prev_input[swap_index +1], prev_input[swap_index]
        print("new input", prev_input)
        
        return prev_input
        

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

            time.sleep(5)

            cityList = []
            for i in range(0, len(self.params)):
                cityList.append(City(self.params[i][0], self.params[i][1]))

            return [None, event_value, Fitness(cityList).routeDistance()]
