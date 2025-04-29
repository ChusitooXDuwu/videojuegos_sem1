import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world:esper.World, deltatime:float):
    components = world.get_components(CSurface, CAnimation)

    for _, (c_surface, c_animation) in components:
        c_animation.current_animation_time -= deltatime
        if c_animation.current_animation_time <= 0:
            c_animation.current_animation_time = c_animation.animations_list[c_animation.current_animation].framerate
            c_animation.curr_frame += 1
            if c_animation.curr_frame > c_animation.animations_list[c_animation.current_animation].end:
                c_animation.curr_frame = c_animation.animations_list[c_animation.current_animation].start
            rect_surf = c_surface.surf.get_rect()
            c_surface.area.w = rect_surf.w / c_animation.frames
            c_surface.area.x = c_surface.area.w * c_animation.curr_frame