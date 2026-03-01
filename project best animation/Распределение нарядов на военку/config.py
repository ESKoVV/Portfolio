# config.py
from styles import Styles

class Config:
    # Default settings
    DEFAULT_TRAINING_DAY = "Monday"
    DEFAULT_DUTY_PER_WEEK = 1
    DEFAULT_VPI_PER_WEEK = 1
    DEFAULT_GUARD_COUNT = 4
    DEFAULT_PEOPLE_COUNT = 20
    DEFAULT_GUARD_FREQUENCY = 2  # weeks - CHANGED FROM DUTY_FREQUENCY
    DEFAULT_FIRST_DUTY_DATE = "2025-11-24"
    
    # Date settings
    START_DATE = "2025-11-24"
    END_DATE = "2025-12-31"
    
    # Use colors from Styles
    COLORS = Styles.COLORS