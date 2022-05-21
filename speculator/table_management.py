from cgitb import lookup
import threading
import time
import sys
import itertools
import difflib

class TableManagement(threading.Thread):
    
    def __init__(self, config_id, fb_dictionary):
        threading.Thread.__init__(self, name=config_id)
        
        self.fb_dictionary = fb_dictionary
        self.wait_event = threading.Event()
        
    def run(self):
        while (True):
            idle_time = True
            
            # checks if there is any function block runnning
            for fb_name, fb_element in self.fb_dictionary.items():
                print("TABLEMG - ", fb_element, "\n")
                
                print(type(fb_element))
                
                # checks only speculable FB's (the heaviest ones)
                if fb_element.speculate_events:
                    if not fb_element.execution_end.is_set():
                        idle_time = False 
                        # break
                
                    
            if idle_time:
                print("iddleee")
                # choose which function block to execute
                selected_fb, selected_event = self.fb_selection()
                
                print("Selected fb ", selected_fb)
                
                if selected_fb != None: 
                    lookup_table = selected_fb.lookup.lookupTable
                    event_table = {k:v for (k,v) in lookup_table.items() if selected_event == k[0]}
                    
                    inputs = list(next(iter(event_table)))
                    
                    while(tuple(inputs) in event_table):   
                        # For each input used to speculate, call its generation function
                        for (index, (var_name, var_generation)) in enumerate(selected_fb.speculate_vars.items()):
                            inputs[index+2] = var_generation(selected_event, event_table, selected_fb.speculate_vars, lookup_table)
                    
                    # executes task with chosen inputssss
                    outputs = selected_fb.fb_obj.schedule(*inputs)
                    
                    # saves outputs in the table
                    selected_fb.lookup.write_entry(inputs, outputs)
                
            self.wait_event.wait(60)
        

def fb_selection(self):
    selected_fb = None
    selected_event = None
    min_table_size = sys.maxsize

    # finds function block that uses the lookup table and has the smallest one
    for fb_name, fb_element in self.fb_dictionary.items():
        for event_name in fb_element.speculate_events:
            print("speculate_events - ", fb_element.speculate_events)
            
            table_size = fb_element.lookup.get_table_event_size(event_name)
            if table_size > 0 and table_size < min_table_size:
                min_table_size = table_size
                selected_fb = fb_element
                selected_event = event_name
    
    return selected_fb, selected_event
