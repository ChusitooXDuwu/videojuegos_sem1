import esper
import pygame


from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.create.prefab_creator import create_enemy, create_hunter



def system_enemy_spawner(world: esper.World, delta_time: float, enemy_data: dict):
    
    components = world.get_component(CEnemySpawner)
    
    c_es: CEnemySpawner
    
    for entity, c_es in components:
        c_es.passed_time += delta_time
        
        for event in c_es.spawn_events:
            if not event["creado"] and c_es.passed_time >= event["time"]:
                
                enemy_type = event["enemy_type"]
                config = enemy_data[enemy_type]
                pos = pygame.Vector2(event["position"]["x"], event["position"]["y"])
                if enemy_type != "Hunter":
                    create_enemy(world, pos, config)
                else:
                     create_hunter(world, pos, config)
                event["creado"] = True

        
        
        
    