import logging
class Lookup:

    def __init__(self):
        self.lookupTable = dict()
        
    def lookup_input(self, input):        
        inputKey = tuple(input)
        
        if inputKey in self.lookupTable:
            return self.lookupTable[inputKey]
        else:
            return None
        # may use generators to join input values
        
    def write_entry(self, input, output):
        # logging.info("Writing entry (%s, %s)", input, output)
        
        inputKey = tuple(input)
        
        self.lookupTable[inputKey] = output
        
    def decision(self, input):
        # logging.info("Table %s", self.lookupTable)
        # logging.info("Speculator decision making for input %s", input)
        
        output = self.lookup_input(input)
        
        if output != None:
            # logging.info("Output %s", output)
            return output
        else:
            # logging.info("Execute task")
            return False
            
    def get_table_event_size(self, event_name):
        # logging.info("Table len %s", len(self.lookupTable))
        event_table = [k for k in self.lookupTable.keys() if event_name == k[0]]
        return len(event_table)