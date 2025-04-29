
import esper
from src.ecs.components.c_special_ability import CSpecialAbility

def system_special_ability_cooldown(world: esper.World, delta_time: float):
    
    components = world.get_component(CSpecialAbility)
    
    for _, special_ability in components:
        if not special_ability.is_ready:
            special_ability.current_cooldown -= delta_time
            if special_ability.current_cooldown <= 0:
                special_ability.current_cooldown = 0
                special_ability.is_ready = True