import datetime
import time


def millis_to_str(millis):
    return datetime.datetime.fromtimestamp(long(millis)).strftime('%Y-%m-%d %H:%M:%S')
    
def get_current_time_str():
    return millis_to_str(long(time.time()))
