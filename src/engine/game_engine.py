import esper
import pygame
import json
import math

from src.create.prefab_creator import crear_cuadrado, create_enemy_spawner, create_input_player, create_player_square
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_player import CTagPlayer

from src.ecs.systems.c_screen_bounce import system_screen_bounce
from src.ecs.systems.s_player_boundary import system_player_boundary
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
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
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.SCALED)
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
        with open("./assets/cfg/cfg_00/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
            self.window_height = self.window_cfg["size"]["h"]
            self.window_width = self.window_cfg["size"]["w"]
            self.window_color_r = self.window_cfg["bg_color"]["r"]
            self.window_color_g = self.window_cfg["bg_color"]["g"]
            self.window_color_b = self.window_cfg["bg_color"]["b"]
            self.window_title = self.window_cfg["title"]
            self.window_fps = self.window_cfg["framerate"]
        with open("./assets/cfg/cfg_00/enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("./assets/cfg/cfg_00/level_01.json") as level_01_file:
            self.level_cfg = json.load(level_01_file)   
        with open("./assets/cfg/cfg_00/player.json") as player_file:
            self.player_cfg = json.load(player_file)
        with open("./assets/cfg/cfg_00/bullet.json") as bullet_file:
            self.bullet_cfg = json.load(bullet_file)

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
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
            
            if "max_bullets" not in self.level_cfg:
                print("Error: max_bullets not found in level config")
                return
                
            if bullet_count < self.level_cfg["max_bullets"]:
                
                if self._player_c_t is None or self._player_c_s is None:
                    print("Error: Player components not found")
                    return
                    
                
                player_pos = self._player_c_t.pos
                player_size = pygame.Vector2(self._player_c_s.surf.get_width(), self._player_c_s.surf.get_height())
                
               
                bullet_size = pygame.Vector2(self.bullet_cfg["size"]["x"], self.bullet_cfg["size"]["y"])
                bullet_pos_x = player_pos.x + (player_size.x / 2) - (bullet_size.x / 2)
                bullet_pos_y = player_pos.y + (player_size.y / 2) - (bullet_size.y / 2)
                bullet_pos = pygame.Vector2(bullet_pos_x, bullet_pos_y)
                
                
                dx = mouse_pos[0] - (player_pos.x + player_size.x / 2)
                dy = mouse_pos[1] - (player_pos.y + player_size.y / 2)
                
               
                magnitude = math.sqrt(dx * dx + dy * dy)
                if magnitude > 0:
                    dx = dx / magnitude
                    dy = dy / magnitude
                
               
                bullet_speed = self.bullet_cfg["speed"]
                bullet_vel = pygame.Vector2(dx * bullet_speed, dy * bullet_speed)
                
                
                bullet_color = pygame.Color(
                    self.bullet_cfg["color"]["r"],
                    self.bullet_cfg["color"]["g"],
                    self.bullet_cfg["color"]["b"]
                )
                
               
                bullet_entity = crear_cuadrado(
                    self.ecs_world, 
                    bullet_size, 
                    bullet_pos, 
                    bullet_vel, 
                    bullet_color
                )
                
                self.ecs_world.add_component(bullet_entity, CTagBullet())
                print(f"Bullet created successfully. Active bullets: {bullet_count + 1}")
        except Exception as e:
            print(f"Error in _fire_bullet: {e}")

    def _update(self):
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)
        system_player_boundary(self.ecs_world, self.screen)
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies_cfg)
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_cfg)
        system_collision_bullet_enemy(self.ecs_world)
        system_screen_boundary_bullet(self.ecs_world, self.screen)
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