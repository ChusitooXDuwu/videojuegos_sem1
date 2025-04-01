
import esper
import pygame
import json

from src.create.prefab_creator import crear_cuadrado, create_enemy_spawner

from src.ecs.systems.c_screen_bounce import system_screen_bounce
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering

from src.ecs.systems.system_enemy_spawner import system_enemy_spawner

f = open('assets/cfg/enemies.json')
enemies_type = json.load(f)
f.close()

g = open('assets/cfg/window.json')
window_cfg = json.load(g)
g.close()

print("ENEMIES TYPE: ", enemies_type)
print("WINDOW CFG: ", window_cfg)
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

        f = open('assets/cfg/enemies.json')
        enemies_type = json.load(f)
        f.close()

        g = open('assets/cfg/window.json')
        window_cfg = json.load(g)
        g.close()

        self.enemies_type = enemies_type
        self.window_cfg = window_cfg

    
        
    def _load_json(self):
        with open("./assets/cfg/cfg_02/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
            self.window_height = self.window_cfg["size"]["h"]
            self.window_width = self.window_cfg["size"]["w"]
            self.window_color_r = self.window_cfg["bg_color"]["r"]
            self.window_color_g = self.window_cfg["bg_color"]["g"]
            self.window_color_b = self.window_cfg["bg_color"]["b"]
            self.window_title = self.window_cfg["title"]
            self.window_fps = self.window_cfg["framerate"]
        with open("./assets/cfg/cfg_02//enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("./assets/cfg/cfg_02//level_01.json") as level_01_file:
            self.level_cfg = json.load(level_01_file)   


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
        create_enemy_spawner(self.ecs_world, self.level_cfg)
        

        crear_cuadrado(self.ecs_world, pygame.Vector2(50, 50), 
                       pygame.Vector2(100, 100), 
                       pygame.Vector2(200, 200), 
                       pygame.Color(255, 0, 0))
    
    
    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0 

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
    

    def _update(self):
       system_movement(self.ecs_world, self.delta_time)
       system_screen_bounce(self.ecs_world, self.screen)
       system_enemy_spawner(self.ecs_world, self.delta_time,self.enemies_type)


    def _draw(self):

        self.screen.fill((self.window_color_r, self.window_color_g, self.window_color_b))
        
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        pygame.quit()
