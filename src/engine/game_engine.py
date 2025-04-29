import asyncio
import esper
import pygame
import json
import math

from src.create.prefab_creator import crear_cuadrado, create_bullet, create_enemy_spawner, create_input_player, create_player_square
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_player import CTagPlayer

from src.ecs.systems.c_screen_bounce import system_screen_bounce
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_collision_hunter_enemy import system_collision_hunter_enemy
from src.ecs.systems.s_explosion_animation_end import system_explosion_animation_end
from src.ecs.systems.s_hunter_state import system_hunter_state
from src.ecs.systems.s_player_boundary import system_player_boundary
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_screen_boundary_bullet import system_screen_boundary_bullet
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.system_enemy_spawner import system_enemy_spawner

class GameEngine:
    def __init__(self) -> None:
        self._load_json()
        pygame.init()
        pygame.display.set_caption(self.window_title)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), 0)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_fps
        self.delta_time = 0

        self.ecs_world = esper.World()
        self._player_entity = None
        self._player_c_v = None
        self._player_c_t = None
        self._player_c_s = None
        
    def _load_json(self):
        with open("./assets/cfg/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
            self.window_height = self.window_cfg["size"]["h"]
            self.window_width = self.window_cfg["size"]["w"]
            self.window_color_r = self.window_cfg["bg_color"]["r"]
            self.window_color_g = self.window_cfg["bg_color"]["g"]
            self.window_color_b = self.window_cfg["bg_color"]["b"]
            self.window_title = self.window_cfg["title"]
            self.window_fps = self.window_cfg["framerate"]
        with open("./assets/cfg/enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("./assets/cfg/level_01.json") as level_01_file:
            self.level_cfg = json.load(level_01_file)   
        with open("./assets/cfg/player.json") as player_file:
            self.player_cfg = json.load(player_file)
        with open("./assets/cfg/bullet.json") as bullet_file:
            self.bullet_cfg = json.load(bullet_file)
        with open("./assets/cfg/explosion.json") as explosion_file:
            self.explosion_cfg = json.load(explosion_file)

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _create(self):
        
        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_cfg)
        
        
        try:
            self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
            self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
            self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
            print("Player components acquired successfully")
        except Exception as e:
            print(f"Error getting player components: {e}")
        
        
        create_enemy_spawner(self.ecs_world, self.level_cfg)
        create_input_player(self.ecs_world)
    
    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0 

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
                self._fire_bullet(pygame.mouse.get_pos())
                
            if event.type == pygame.QUIT:
                self.is_running = False
    
    def _fire_bullet(self, mouse_pos):
        
        try:
            bullet_count = len(list(self.ecs_world.get_components(CTagBullet)))
            
            if "max_bullets" not in self.level_cfg["player_spawn"]:
                print("Error: max_bullets not found in level config")
                return
                
            if bullet_count < self.level_cfg["player_spawn"]["max_bullets"]:
                
                if self._player_c_t is None or self._player_c_s is None:
                    print("Error: Player components not found")
                    return
                    
                
                create_bullet(self.ecs_world, 
                                    mouse_pos, 
                                    self._player_c_t.pos,
                                    self.bullet_cfg, 
                                    self._player_c_s.area.size)
                print(f"Bullet created successfully. Active bullets: {bullet_count + 1}")
        except Exception as e:
            print(f"Error in _fire_bullet: {e}")

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies_cfg)
        system_movement(self.ecs_world, self.delta_time)
        system_player_state(self.ecs_world)
        system_hunter_state(self.ecs_world, self._player_entity, self.enemies_cfg["Hunter"])
        system_screen_bounce(self.ecs_world, self.screen)
        system_player_boundary(self.ecs_world, self.screen)
        system_screen_boundary_bullet(self.ecs_world, self.screen)
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_cfg, self.explosion_cfg)
        system_collision_bullet_enemy(self.ecs_world, self.explosion_cfg)
        system_collision_hunter_enemy(self.ecs_world, self.explosion_cfg)
        system_explosion_animation_end(self.ecs_world)
        system_animation(self.ecs_world, self.delta_time)

        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill((self.window_color_r, self.window_color_g, self.window_color_b))
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input:CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]