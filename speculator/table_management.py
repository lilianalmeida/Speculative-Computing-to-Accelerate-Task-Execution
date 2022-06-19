import threading
import sys
import logging

class TableManagement(threading.Thread):
    
    def __init__(self, config_id, fb_dictionary):
        threading.Thread.__init__(self, name=(config_id + '_tableManagement'))
        
        self.fb_dictionary = fb_dictionary
        self.wait_event = threading.Event()
        
    def run(self):
        has_speculative_FBs = False
        
        while (True):
            idle_time = True
            
            # checks if there is any function block runnning
            for fb_name, fb_element in self.fb_dictionary.items():
                
                # checks only speculable FB's (the heaviest ones)
                if fb_element.speculate_events:
                    
                    if not has_speculative_FBs:
                        has_speculative_FBs = True
                    
                    if fb_element.execution_end.is_set():
                        idle_time = False 
                        break
            
            # breaks while loop if it doesn't have any speculative FB
            if not has_speculative_FBs:
                break
                    
            if idle_time:
                
                # choose which function block to execute
                exists, selected_fb, selected_event = self.fb_selection()
                
                # end thread if FBs stopped working
                if not exists:
                    break
                
                if selected_fb != None:  
                    logging.info('executing fb %s in idle times...', selected_fb)
                    
                    lookup_table = selected_fb.lookup.lookupTable
                    event_table = {k:v for (k,v) in lookup_table.items() if selected_event == k[0]}
                    
                    inputs = list(next(iter(event_table)))
                    
                    while(tuple(inputs) in event_table): 
                        
                        # For each input used to speculate, call its generation function
                        for (index, (var_name, var_generation)) in enumerate(selected_fb.speculate_vars.items()):
                            try:
                                inputs[index+2] = var_generation(selected_event, index+2, event_table, selected_fb.speculate_vars, lookup_table)
                            except Exception as e: 
                                logging.error("%s", e)
                    
                    # executes task with chosen inputssss
                    try:
                        outputs = selected_fb.fb_obj.schedule(*inputs)
                    except Exception as e: 
                        logging.error("%s", e)
                            
                    # saves outputs in the table
                    selected_fb.lookup.write_entry(inputs, outputs)
                    
                    for speculator in selected_fb.speculate_events[selected_event]:
                        speculator("TRAIN_STREAM", inputs, outputs, None)

            self.wait_event.wait(10)
        

    def fb_selection(self):
        selected_fb = None
        selected_event = None
        exists = True
        min_table_size = sys.maxsize

        # finds function block that uses the lookup table and has the smallest one
        for fb_name, fb_element in self.fb_dictionary.items():
            
            # verifies whether the FB is no longer working
            if fb_element.kill_event.is_set():
                exists = False
                break
            
            for event_name in fb_element.speculate_events:
                
                table_size = fb_element.lookup.get_table_event_size(event_name)
                
                if table_size > 0 and table_size < min_table_size:
                    min_table_size = table_size
                    selected_fb = fb_element
                    selected_event = event_name
        
        return exists, selected_fb, selected_event
