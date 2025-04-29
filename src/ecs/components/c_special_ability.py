
class CSpecialAbility:
    """Component that handles special ability state and cooldown"""
    def __init__(self, cooldown_time=5.0):
        self.cooldown_time = cooldown_time  
        self.current_cooldown = 0.0  
        self.is_ready = True  