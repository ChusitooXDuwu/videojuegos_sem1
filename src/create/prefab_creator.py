import math
import esper
import pygame
import random

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_special_ability import CSpecialAbility
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_hunter import CTagHunter
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator

def create_bullet(ecs_world:esper.World, end_pos:pygame.Vector2, start_pos:pygame.Vector2, bullet_info:dict, player_size:pygame.Vector2):
    bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    
    size = bullet_surface.get_rect().size
    pos = pygame.Vector2(start_pos.x + (player_size[0] / 2) - (size[0] / 2), 
                         start_pos.y + (player_size[1] / 2) - (size[1] / 2))
    direction = (end_pos - start_pos).normalize()
    vel = direction * bullet_info["velocity"]
    bullet_entity = create_sprite(ecs_world, pos, vel, bullet_surface)
    ecs_world.add_component(bullet_entity, CTagBullet())  
    ServiceLocator.sounds_service.play(bullet_info["sound"])




def create_enemy(ecs_world:esper.World, pos:pygame.Vector2, enemy_info:dict):
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    

    vel_max = enemy_info["velocity_max"]
    vel_min = enemy_info["velocity_min"]
    vel_x = random.uniform(vel_min, vel_max)
    vel_y = random.uniform(vel_min, vel_max)
    vel = pygame.Vector2(vel_x, vel_y)
    enemy_entity = create_sprite(ecs_world, pos, vel, enemy_surface) 
    ecs_world.add_component(enemy_entity, CTagEnemy())
    ServiceLocator.sounds_service.play(enemy_info["sound"])

def crear_cuadrado(ecs_world:esper.World,
                   size:pygame.Vector2,
                   pos:pygame.Vector2,
                   vel:pygame.Vector2,
                   col:pygame.Color):
    
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity, 
                                     CSurface(size,col))
    ecs_world.add_component(cuad_entity,
                                     CTransform(pos))
    ecs_world.add_component(cuad_entity,
                                     CVelocity(vel))
    return cuad_entity
    
def create_enemy_spawner(ecs_world:esper.World, level_cfg:dict) -> None:
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(spawner_entity, CEnemySpawner(level_cfg))


def create_player_square(ecs_world:esper.World, player_cfg:dict, level_cfg:dict) -> int:

    player_surface = ServiceLocator.images_service.get(player_cfg["image"])
    
    size = player_surface.get_size()
    size = pygame.Vector2(size[0] / player_cfg["animations"]["number_frames"], size[1])
    pos = pygame.Vector2(level_cfg["player_spawn"]["position"]["x"] - (size.x / 2),
                         level_cfg["player_spawn"]["position"]["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = create_sprite(ecs_world, pos, vel, player_surface)
    ecs_world.add_component(player_entity, CTagPlayer())
    ecs_world.add_component(player_entity, CAnimation(player_cfg["animations"]))
    ecs_world.add_component(player_entity, CPlayerState())

    special_ability_cooldown = 5.0  # 5 seconds cooldown
    ecs_world.add_component(player_entity, CSpecialAbility(special_ability_cooldown))
    
    return player_entity


def activate_special_ability(ecs_world: esper.World, player_entity: int, bullet_cfg: dict):
    """Creates bullets in four directions (N, S, E, W) as a special ability"""
    
    if not ecs_world.entity_exists(player_entity):
        print("Player entity does not exist")
        return False
        
   
    try:
        c_transform = ecs_world.component_for_entity(player_entity, CTransform)
        c_surface = ecs_world.component_for_entity(player_entity, CSurface)
        c_special = ecs_world.component_for_entity(player_entity, CSpecialAbility)
    except KeyError:
        print("Missing required components for special ability")
        return False
    
    
    if not c_special.is_ready:
        print("Special ability on cooldown")
        return False
    
    
    player_pos = c_transform.pos
    center_x = player_pos.x + (c_surface.area.width / 2)
    center_y = player_pos.y + (c_surface.area.height / 2)
    player_center = pygame.Vector2(center_x, center_y)
    
    # Define the four directions (North, East, South, West)
    directions = [
        pygame.Vector2(0, -1),  
        pygame.Vector2(1, 0),   
        pygame.Vector2(0, 1),   
        pygame.Vector2(-1, 0)   
    ]
    
    
    for direction in directions:
       
        target_pos = player_center + direction * 1000 
        
       
        create_bullet(
            ecs_world,
            target_pos,
            player_pos,
            bullet_cfg,
            c_surface.area.size
        )
    
    
    c_special.is_ready = False
    c_special.current_cooldown = c_special.cooldown_time
    
    
    if "special_sound" in bullet_cfg:
        ServiceLocator.sounds_service.play(bullet_cfg["special_sound"])
    else:
        
        ServiceLocator.sounds_service.play(bullet_cfg["sound"])
    
    return True


def create_input_player(ecs_world:esper.World):
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()
    input_fire = ecs_world.create_entity()


    ecs_world.add_component(input_right,
                            CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    ecs_world.add_component(input_up,
                            CInputCommand("PLAYER_UP", pygame.K_UP))
    ecs_world.add_component(input_down,
                            CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
    ecs_world.add_component(input_left, 
                            CInputCommand("PLAYER_LEFT", pygame.K_LEFT))


def create_sprite(ecs_world:esper.World, pos:pygame.Vector2, vel: pygame.Vector2, surface:pygame.Surface) -> int:
    sprite_entity = ecs_world.create_entity()
    ecs_world.add_component(sprite_entity, 
                            CTransform(pos))
    ecs_world.add_component(sprite_entity, 
                            CVelocity(vel))
    ecs_world.add_component(sprite_entity, 
                            CSurface.from_surface(surface))
    return sprite_entity

def create_hunter(ecs_world:esper.World, pos:pygame.Vector2, hunter_info:dict):

    hunter_surface = ServiceLocator.images_service.get(hunter_info["image"])
    
    vel = pygame.Vector2(0, 0)
    enemy_entity = create_sprite(ecs_world, pos, vel, hunter_surface)
    ecs_world.add_component(enemy_entity, CAnimation(hunter_info["animations"]))
    ecs_world.add_component(enemy_entity, CHunterState(pos))
    ecs_world.add_component(enemy_entity, CTagEnemy())
    ecs_world.add_component(enemy_entity, CTagHunter())


def create_explosion(world:esper.World, pos:pygame.Vector2, explosion_info:dict) -> int:
    explosion_surface = ServiceLocator.images_service.get(explosion_info["image"])
    
    vel = pygame.Vector2(0, 0)
    explosion_entity = create_sprite(world, pos, vel, explosion_surface)
    world.add_component(explosion_entity,
                        CAnimation(explosion_info["animations"]))
    world.add_component(explosion_entity, CTagExplosion())

    ServiceLocator.sounds_service.play(explosion_info["sound"])
    return explosion_entity
