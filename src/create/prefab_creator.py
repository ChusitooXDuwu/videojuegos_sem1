import math
import esper
import pygame
import random

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer

def create_bullet(ecs_world: esper.World, 
                 player_pos: pygame.Vector2, 
                 player_size: pygame.Vector2,
                 mouse_pos: tuple,
                 bullet_cfg: dict) -> int:
  
    bullet_size = pygame.Vector2(bullet_cfg["size"]["x"], bullet_cfg["size"]["y"])
    bullet_pos_x = player_pos.x + (player_size.x / 2) - (bullet_size.x / 2)
    bullet_pos_y = player_pos.y + (player_size.y / 2) - (bullet_size.y / 2)
    bullet_pos = pygame.Vector2(bullet_pos_x, bullet_pos_y)
    
    
    dx = mouse_pos[0] - (player_pos.x + player_size.x / 2)
    dy = mouse_pos[1] - (player_pos.y + player_size.y / 2)
    
    
    magnitude = math.sqrt(dx * dx + dy * dy)
    if magnitude > 0:
        dx = dx / magnitude
        dy = dy / magnitude
    
    
    bullet_speed = bullet_cfg["speed"]
    bullet_vel = pygame.Vector2(dx * bullet_speed, dy * bullet_speed)
    
    
    bullet_color = pygame.Color(
        bullet_cfg["color"]["r"],
        bullet_cfg["color"]["g"],
        bullet_cfg["color"]["b"]
    )
    
    
    bullet_entity = crear_cuadrado(
        ecs_world, 
        bullet_size, 
        bullet_pos, 
        bullet_vel, 
        bullet_color
    )
    
    # Add bullet tag
    ecs_world.add_component(bullet_entity, CTagBullet())
    
    return bullet_entity


def create_enemy(ecs_world:esper.World, pos:pygame.Vector2, enemy_info:dict):
    size = pygame.Vector2(enemy_info["size"]["x"], enemy_info["size"]["y"])
    col = pygame.Color(enemy_info["color"]["r"],enemy_info["color"]["g"],enemy_info["color"]["b"])
    vel_max = enemy_info["velocity_max"]
    vel_min = enemy_info["velocity_min"]
    vel_x = random.uniform(vel_min, vel_max)
    vel_y = random.uniform(vel_min, vel_max)
    vel = pygame.Vector2(vel_x, vel_y)
    enemy_entity = crear_cuadrado(ecs_world, size, pos, vel, col)  
    ecs_world.add_component(enemy_entity, CTagEnemy())

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
    size = pygame.Vector2(player_cfg["size"]["x"],
                           player_cfg["size"]["y"])
    color = pygame.Color(player_cfg["color"]["r"],
                         player_cfg["color"]["g"],
                         player_cfg["color"]["b"])
    pos = pygame.Vector2(level_cfg["player_spawn"]["position"]["x"] - (size.x / 2),
                         level_cfg["player_spawn"]["position"]["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = crear_cuadrado(ecs_world, size, pos, vel, color)
    ecs_world.add_component(player_entity, CTagPlayer())
    return player_entity

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


