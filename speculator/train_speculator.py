import logging
import threading

class TrainSpeculator(threading.Thread):

    def __init__(self, config_id, fb_dictionary):
        threading.Thread.__init__(self, name=(config_id + '_trainSpeculator'))
        
        self.fb_dictionary = fb_dictionary
        self.wait_event = threading.Event()
        
        
    def run(self):
        has_speculative_FBs = False
        
        while (True):
            
            logging.info("\n\n\n\nTrainS\n\n")
            
            for fb_element in self.fb_dictionary.values():
                
                # checks only speculable FB's
                if fb_element.speculate_events:
                
                    if not has_speculative_FBs:
                        has_speculative_FBs = True
                    
                    # trains in batch for all existing events and speculators for the current FB
                    for event, speculators_array in fb_element.speculate_events.items():
                        
                        lookup_table = fb_element.lookup.lookupTable
                        event_table = {k:v for (k,v) in lookup_table.items() if event == k[0]}
                        
                        for speculator in speculators_array:
                            speculator("TRAIN_BATCH", None, None, event_table)
            
            # breaks while loop if it doesn't have any speculative FB
            if not has_speculative_FBs:
                break

            self.wait_event.wait(60)
    