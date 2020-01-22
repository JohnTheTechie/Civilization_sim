import threading
import time


class GameClock(threading.Thread):
    """
    configurable clock tick generator

    this clock  holds references of the objects which have registered themselves for clock ticks
        on the set intervals, the clock disburses the ticks to the registered listeners
    the clock frequency could be adjusted in runtime
    The clock frequency is global
    Only one instance of clock will be available for the entire application
    """

    __clock = None

    def __init__(self):
        super().__init__()
        # duration of each tick of the clock
        self.__clock_tick_duration_seconds = 1
        # objects registered to receive the tick
        self.__listening_objects = []
        # duration for next tick
        # initially set equal to the self.__clock_tick_duration_milliseconds
        self.__next_tick = self.__clock_tick_duration_seconds
        # control flag for run
        # need to be set true before start command
        self.clock_control_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__clock is None:
            cls.__clock = object.__new__(cls)
        return cls.__clock

    def register_tick_listener(self, listener):
        """
        register for clock tick

        Any object which extends the clock_listener can and must register themselves for
        clock updates
        On the specified intervals, the tick shall be intimated to the listeners
        when the tick updates are not anymore needed the object must unregister using unregister_tick_listener

        :param listener: object registering for ticks
        :return: None
        """
        if listener is not None and listener not in self.__listening_objects:
            self.__listening_objects.append(listener)

    def unregister_tick_listener(self, listener):
        """
        unregister for clock tick

        :param listener: unregistering object
        :return: None
        """
        if listener is not None and listener in self.__listening_objects:
            self.__listening_objects.remove(listener)

    def set_clock_rate(self, freq_in_hertz = 1):
        """
        change the frequency of the clock

        :param freq_in_hertz: frequency in hertz
        :return: None
        """
        self.__clock_tick_duration_seconds = 1 / freq_in_hertz

    def start_clock(self):
        """
        To be called to start the clock

        when the clock is not needed anymore globally, stop_clock must be called

        :return: None
        """
        # the control flag is set to True so that the clock can run
        self.clock_control_flag = True
        self.start()

    def stop_clock(self):
        """
        stop the clock

        :return:
        """
        # the control flag is set to False. So in the next iteration, the while loop in run shall exit
        self.clock_control_flag = False
        # the next_tick variable set back to full duration of the frequency
        self.__next_tick = self.__clock_tick_duration_seconds

    def run(self):
        # the working of the tick generator is as below
        #   when the clock is started the control flag is set to True
        #   As long as the control flog is True, the while loop will run
        #   calling the stop_clock function will set control flag to False, which will terminate loop
        #   Once inside the loop, first the thread will wait for a duration of self.__next_tick
        #   When start_clock is called, the self.__next_tick will be a full duration of the frequency
        #   Once wait is done, the time stamp will be stored and jobs shall be done
        #   Assumption is job shall be done within the frequency duration
        #   Once job is done, the remaining time, after the time taken for execution of job, is set to self.__next_tick
        #   The calculation of the remaining time is calculated by __calculate_next_tick
        while self.clock_control_flag:
            time.sleep(self.__next_tick)
            ref_time = time.time()
            threading.Thread(target=self.__intimate_listeners).start()
            self.__calculate_next_tick(ref_time)

    def __calculate_next_tick(self, ref_time_stamp):
        """
        calculates the remaining time after the time consumed for execution of jobs

        :param ref_time_stamp: the time stamp immediately taken after the sleep is over
        :return: None
        """
        # The remaining time is calculated as follows
        #   The ref time marks the start of job execution
        #   time consumed by job is current time minus the ref time
        #   Thus the remaining time is the difference between the consumed time and the frequency time
        # If the job consumes more time than the frequency allows, the calculated time will be negative
        # In that case, the next_tick shall be set to zero forcing zero sleep and immediate execution of next iteration
        next_tick = self.__clock_tick_duration_seconds - (time.time() - ref_time_stamp)
        self.__next_tick = 0 if next_tick < 0 else next_tick

    def __intimate_listeners(self):
        # TODO: implement broadcast
        pass
