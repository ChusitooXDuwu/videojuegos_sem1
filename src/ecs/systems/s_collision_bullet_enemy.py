import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet

def system_collision_bullet_enemy(world: esper.World) -> None:
    """
    System that handles collisions between bullets and enemies
    Both the bullet and the enemy are destroyed on collision
    """
    
    bullet_components = world.get_components(CSurface, CTransform, CTagBullet)
    
    
    enemy_components = world.get_components(CSurface, CTransform, CTagEnemy)
    
    
    entities_to_delete = set()
    
    
    for bullet_entity, (bullet_s, bullet_t, _) in bullet_components:
        if bullet_entity in entities_to_delete:
            continue
            
        bullet_rect = bullet_s.surf.get_rect(topleft=bullet_t.pos)
        
        for enemy_entity, (enemy_s, enemy_t, _) in enemy_components:
            if enemy_entity in entities_to_delete:
                continue
                
            enemy_rect = enemy_s.surf.get_rect(topleft=enemy_t.pos)
            
           
            if bullet_rect.colliderect(enemy_rect):
                entities_to_delete.add(bullet_entity)
                entities_to_delete.add(enemy_entity)
                break
    
    
    for entity in entities_to_delete:
        world.delete_entity(entity)