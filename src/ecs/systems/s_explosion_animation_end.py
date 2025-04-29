import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion


def system_explosion_animation_end(world: esper.World):
    components = world.get_components(CTagExplosion, CAnimation)
    for entity, (_, c_animation) in components:
        if c_animation.curr_frame == c_animation.animations_list[c_animation.current_animation].end:
            world.delete_entity(entity)