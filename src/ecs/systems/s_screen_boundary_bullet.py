import esper
import pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet

def system_screen_boundary_bullet(world: esper.World, screen: pygame.Surface):
    """
    System that checks if bullets are out of screen boundaries and removes them if they are
    """
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagBullet)

    c_t: CTransform
    c_s: CSurface
    
    for entity, (c_t, c_s, _) in components:
        bullet_rect = c_s.surf.get_rect(topleft=c_t.pos)
        
        
        if (bullet_rect.right < 0 or 
            bullet_rect.left > screen_rect.width or 
            bullet_rect.bottom < 0 or 
            bullet_rect.top > screen_rect.height):
            world.delete_entity(entity)