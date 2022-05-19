
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
        print("Writing entry (", input, ', ', output, ")")
        
        inputKey = tuple(input)
        
        self.lookupTable[inputKey] = output
        
    def decision(self, input):
        print("Speculator decision making for input ", input)
        
        output = self.lookup_input(input)
        
        if output != None:
            print("Output ", output)
            return output
        else:
            print("Execute task")
            return False
            
    def get_table_size(self):
        return len(self.lookupTable)