import pygame 
import esper
import json




class CEnemySpawner:
    
  

    def __init__(self,spawn_data: dict) -> None:

        spawn_events = spawn_data["enemy_spawn_events"]

        self.spawn_events = [
            {**event, "creado": False} for event in spawn_events
        ]
    
    
        
        self.passed_time = 0.0
        


#
