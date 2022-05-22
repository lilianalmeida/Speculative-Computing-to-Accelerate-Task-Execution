import threading
import logging
from core import fb_interface
from speculator import lookup
import time


class FB(threading.Thread, fb_interface.FBInterface):

    def __init__(self, fb_name, fb_type, fb_obj, fb_xml, input_gen_obj, monitor=None):
        threading.Thread.__init__(self, name=fb_name)
        fb_interface.FBInterface.__init__(self, fb_name, fb_type, fb_xml, input_gen_obj, monitor)

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
            
            # ignores input event id, extracting the event name and variables values
            # inputParams = list(inputs)
            # del inputParams[1]
            
            # if event is supposed to be speculated, checks whether there is an output or if the task needs to be executed
            if eventName in self.speculate_events:
                speculatedOutput = self.lookup.decision(inputs)
                

            try:
                # uses previous output if already calculated
                if speculatedOutput != None and speculatedOutput != False:
                    # logging.info("Use speculated output which is %s", speculatedOutput)
                    outputs = speculatedOutput
            
                else:   
                    # executes task
                    outputs = self.fb_obj.schedule(*inputs)
                    
                    # saves new calculated value in the table
                    if eventName in self.speculate_events:
                        self.lookup.write_entry(inputs, outputs)

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

