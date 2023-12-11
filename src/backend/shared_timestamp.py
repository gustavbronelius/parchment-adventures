# SharedTimestamp.py

from datetime import datetime

class SharedTimestamp:
    current_timestamp = None

    @classmethod
    def set_timestamp(cls):
        cls.current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate and set the timestamp
        #print(f"[SharedTimeStamp] Timestamp set: {cls.current_timestamp}")  # Debug information

    @classmethod
    def get_timestamp(cls):
        #print(f"[SharedTimeStamp] Retrieved timestamp: {cls.current_timestamp}")  # Debug information
        return cls.current_timestamp  # Return the current timestamp

    @classmethod
    def reset_timestamp(cls):
        #print(f"[SharedTimeStamp] Timestamp reset from: {cls.current_timestamp}")  # Debug information before reset
        cls.current_timestamp = None  # Reset the timestamp
        #print(f"[SharedTimeStamp] Timestamp reset to: {cls.current_timestamp}")  # Debug information after reset
