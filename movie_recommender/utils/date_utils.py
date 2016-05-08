import datetime
import time

"""
    Util methods for datetime. 
"""

"""
Convert time in millis to YYYY-dd-mm HH:MM:SS format str.
"""
def millis_to_str(millis):
    return datetime.datetime.fromtimestamp(long(millis)).strftime('%Y-%m-%d %H:%M:%S')
    
"""
Returns current time in YYYY-dd-mm HH:MM:SS format str.
"""
def get_current_time_str():
    return millis_to_str(long(time.time()))
