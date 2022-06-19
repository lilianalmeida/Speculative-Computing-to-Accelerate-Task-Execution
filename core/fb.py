import threading
import logging
from core import fb_interface
from speculator import lookup
import sys


class FB(threading.Thread, fb_interface.FBInterface):

    def __init__(self, fb_name, fb_type, fb_obj, fb_xml, input_gen_obj, speculators_obj,  monitor=None):
        threading.Thread.__init__(self, name=fb_name)
        fb_interface.FBInterface.__init__(self, fb_name, fb_type, fb_xml, input_gen_obj,speculators_obj, monitor)

        self.fb_obj = fb_obj
        self.kill_event = threading.Event()
        self.execution_end = threading.Event()
        self.ua_variables_update = None
        self.lookup = lookup.Lookup()
        

    def run(self):
        logging.info('fb {0} started.'.format(self.fb_name))

        while not self.kill_event.is_set():
            
            # clears the event when starts the execution
            self.execution_end.clear()

            self.wait_event()

            if self.kill_event.is_set():
                break

            inputs = self.read_inputs()
            
            eventName = inputs[0]
            speculatedOutput = None
            
            logging.info('running fb...')
            
            # if event is supposed to be speculated, checks whether there is an output or if the task needs to be executed
            if eventName in self.speculate_events:
                logging.info("Checking lookup table")
                speculatedOutput = self.lookup.decision(inputs)
                

            try:
                # uses previous output if already calculated
                if speculatedOutput != None and speculatedOutput != False:
                    logging.info("Use speculated output which is %s", speculatedOutput)
                    outputs = speculatedOutput
            
                else:  
                    bestOutput = None
                    bestConfidenceLevel = sys.float_info.max
                    
                    logging.info("EVENTS %s %s", eventName, self.speculate_events)
                    
                    if eventName in self.speculate_events:
                        # run all speculators
                        for speculator in self.speculate_events[eventName]:
                            spec_result = speculator("PREDICT", inputs, None, None)
                            
                            if spec_result != None:
                                output, confidenceLevel = spec_result
                                logging.info("OUTPUT for a speculator %s confidence level %s", output, confidenceLevel)
                                
                                # keep if it has a higher confidence level
                                if output != None and confidenceLevel < bestConfidenceLevel:
                                    bestOutput = output
                                    bestConfidenceLevel = confidenceLevel
                        
                        logging.info("BEST OUTPUT %s ", bestOutput)
                    
                    # if all speculators return None, execute task
                    if bestOutput == None:
                        # executes task
                        outputs = self.fb_obj.schedule(*inputs)
                        
                        # saves new calculated value in the table and sim
                        if eventName in self.speculate_events:
                            self.lookup.write_entry(inputs, outputs)
                            
                            for speculator in self.speculate_events[eventName]:
                                speculator("TRAIN_STREAM", inputs, outputs, None)
                    else:
                        # Add output event info to final output array
                        prev_output = next(v for  (k,v) in self.lookup.lookupTable.items() if k[0] == eventName)
                        outputs = prev_output[:2]
                        outputs.extend(bestOutput)
                        
                        logging.info("FINAL OUTPUT %s ", outputs)

            except TypeError as error:
                logging.error('invalid number of arguments (check if fb method args are in fb_type.fbt)')
                logging.exception(error)
                logging.error(error)
                # Stops the thread
                logging.info('stopping the fb work...')
                break

            except Exception as ex:
                logging.error(ex)
                logging.exception(ex)
                # Stops the thread
                logging.info('stopping the fb work...')
                break

            else:
                # If the thread blocks inside any fb method
                if self.kill_event.is_set():
                    break

                self.update_outputs(outputs)

                # updates the opc-ua interface
                if self.ua_variables_update is not None:
                    self.ua_variables_update()

                # sends a signal when ends execution
                self.execution_end.set()

    def stop(self):

        self.stop_thread = True

        self.kill_event.set()
        self.push_event('unblock', 1)

        try:
            self.fb_obj.__del__()
        except AttributeError as exc:
            logging.warning('can not delete the fb object.')
            logging.warning(exc)

        logging.info('fb {0} stopped.'.format(self.fb_name))

