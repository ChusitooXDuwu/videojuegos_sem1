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
from src.engine.service_locator import ServiceLocator
from src.ecs.components.c_special_ability import CSpecialAbility
from src.ecs.systems.s_special_ability_cooldown import system_special_ability_cooldown
from src.ecs.systems.s_render_cooldown_bar import system_render_cooldown_bar
from src.create.prefab_creator import activate_special_ability

class GameEngine:
    # In the __init__ method, add these lines:
    def __init__(self) -> None:
        self._load_json()
        pygame.init()
        pygame.display.set_caption(self.window_title)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), 0)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.is_paused = False
        self.framerate = self.window_fps
        self.delta_time = 0

        # Initialize UI elements from interface.json
        self._init_ui()
        
        # Special ability variables - 5 second cooldown
        self.special_ability_cooldown = 5.0
        self.special_ability_timer = 0.0
        self.special_ability_ready = True

        self.ecs_world = esper.World()
        self._player_entity = None
        self._player_c_v = None
        self._player_c_t = None
        self._player_c_s = None
        
        # Create game entities
        self._create()


    def _init_ui(self):
        """Initialize UI elements from interface.json"""
        try:
            # Load interface configuration
            with open("./assets/cfg/interface.json") as interface_file:
                self.interface_cfg = json.load(interface_file)
                
            # Create title text
            if "title" in self.interface_cfg:
                title_cfg = self.interface_cfg["title"]
                
                # Use system font since we don't have a specific font file
                title_font = pygame.font.SysFont("Arial", title_cfg["size"], bold=True)
                
                # Create title surface
                title_color = pygame.Color(
                    title_cfg["color"][0], 
                    title_cfg["color"][1], 
                    title_cfg["color"][2]
                )
                self.title_text = title_font.render(title_cfg["text"], True, title_color)
                self.title_rect = self.title_text.get_rect(topleft=(title_cfg["position"]["x"], title_cfg["position"]["y"]))
                
            # Create pause text
            if "pause" in self.interface_cfg:
                pause_cfg = self.interface_cfg["pause"]
                
                # Use system font
                pause_font = pygame.font.SysFont("Arial", pause_cfg["size"], bold=True)
                
                # Create pause surface
                pause_color = pygame.Color(
                    pause_cfg["color"][0], 
                    pause_cfg["color"][1], 
                    pause_cfg["color"][2]
                )
                self.pause_text = pause_font.render(pause_cfg["text"], True, pause_color)
                self.pause_rect = self.pause_text.get_rect(center=(pause_cfg["position"]["x"], pause_cfg["position"]["y"]))
                
            # Create instruction texts
            if "instructions" in self.interface_cfg:
                instr_cfg = self.interface_cfg["instructions"]
                
                # Movement instructions
                if "move" in instr_cfg:
                    move_cfg = instr_cfg["move"]
                    move_font = pygame.font.SysFont("Arial", move_cfg["size"])
                    move_color = pygame.Color(
                        move_cfg["color"][0], 
                        move_cfg["color"][1], 
                        move_cfg["color"][2]
                    )
                    self.instr1_text = move_font.render(move_cfg["text"], True, move_color)
                    self.instr1_rect = self.instr1_text.get_rect()
                    self.instr1_rect.bottomright = (move_cfg["position"]["x"], move_cfg["position"]["y"])
                    
                # Shoot instructions
                if "shoot" in instr_cfg:
                    shoot_cfg = instr_cfg["shoot"]
                    shoot_font = pygame.font.SysFont("Arial", shoot_cfg["size"])
                    shoot_color = pygame.Color(
                        shoot_cfg["color"][0], 
                        shoot_cfg["color"][1], 
                        shoot_cfg["color"][2]
                    )
                    self.instr2_text = shoot_font.render(shoot_cfg["text"], True, shoot_color)
                    self.instr2_rect = self.instr2_text.get_rect()
                    self.instr2_rect.bottomright = (shoot_cfg["position"]["x"], shoot_cfg["position"]["y"])
                    
                # Special ability instructions
                if "special" in instr_cfg:
                    special_cfg = instr_cfg["special"]
                    special_font = pygame.font.SysFont("Arial", special_cfg["size"])
                    special_color = pygame.Color(
                        special_cfg["color"][0], 
                        special_cfg["color"][1], 
                        special_cfg["color"][2]
                    )
                    self.instr3_text = special_font.render(special_cfg["text"], True, special_color)
                    self.instr3_rect = self.instr3_text.get_rect()
                    self.instr3_rect.bottomright = (special_cfg["position"]["x"], special_cfg["position"]["y"])
                
            # Load cooldown bar configuration
            if "cooldown" in self.interface_cfg:
                cooldown_cfg = self.interface_cfg["cooldown"]
                self.cooldown_bar_width = cooldown_cfg["width"]
                self.cooldown_bar_height = cooldown_cfg["height"]
                self.cooldown_bar_position = (cooldown_cfg["position"]["x"], cooldown_cfg["position"]["y"])
            else:
                # Default cooldown bar settings
                self.cooldown_bar_width = 100
                self.cooldown_bar_height = 15
                self.cooldown_bar_position = (20, self.window_height - 25)
                
            print("UI elements loaded from interface.json successfully")
            
        except Exception as e:
            print(f"Error loading UI from interface.json: {e}")
            # Create fallback UI elements
            fallback_font = pygame.font.SysFont("Arial", 28, bold=True)
            self.title_text = fallback_font.render("Entrega 4 Chu", True, (64, 196, 255))
            self.title_rect = self.title_text.get_rect(topleft=(20, 15))
            
            pause_font = pygame.font.SysFont("Arial", 48, bold=True)
            self.pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
            self.pause_rect = self.pause_text.get_rect(center=(self.window_width // 2, self.window_height // 2))
            
            instr_font = pygame.font.SysFont("Arial", 16)
            self.instr1_text = instr_font.render("Movimiento: Flechas", True, (255, 220, 100))
            self.instr1_rect = self.instr1_text.get_rect()
            self.instr1_rect.bottomright = (self.window_width - 20, self.window_height - 40)
            
            self.instr2_text = instr_font.render("Disparo: Ratón", True, (100, 255, 100))
            self.instr2_rect = self.instr2_text.get_rect()
            self.instr2_rect.bottomright = (self.window_width - 20, self.window_height - 20)
            
            self.instr3_text = instr_font.render("Poder: Spacebar, Pausa: P", True, (255, 150, 150))
            self.instr3_rect = self.instr3_text.get_rect()
            self.instr3_rect.bottomright = (self.window_width - 20, self.window_height)
            
            # Default cooldown bar settings
            self.cooldown_bar_width = 100
            self.cooldown_bar_height = 15
            self.cooldown_bar_position = (20, self.window_height - 25)
            
            print("Using fallback UI elements")


        
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

        # In the _load_json method, add:
        try:
            with open("./assets/cfg/interface.json") as interface_file:
                self.interface_cfg = json.load(interface_file)
        except Exception as e:
            print(f"Error loading interface config: {e}")
            # Create minimal default interface config
            self.interface_cfg = {
                "font": None,
                "pause": {
                    "text": "PAUSED",
                    "color": [255, 255, 255],
                    "size": 48,
                    "position": {
                        "x": self.window_width // 2,
                        "y": self.window_height // 2
                    }
                }
            }    

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
        
        existing_player = False
        for _, _ in self.ecs_world.get_components(CTagPlayer):
            existing_player = True
            break
        
        
        if not existing_player:
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
            
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.is_paused = not self.is_paused
                print(f"Game {'paused' if self.is_paused else 'resumed'}")
            
           
            if not self.is_paused and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._activate_special_ability()
            
            
            if not self.is_paused and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
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
    
        if not self.is_paused:
        # Update special ability cooldown
            if not self.special_ability_ready:
                self.special_ability_timer -= self.delta_time
                if self.special_ability_timer <= 0:
                    self.special_ability_timer = 0
                    self.special_ability_ready = True
                    print("Special ability ready!")
            
            # Regular game systems
            system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies_cfg)
            system_movement(self.ecs_world, self.delta_time)
            system_player_state(self.ecs_world, self.player_cfg)  # Pass player_cfg for movement sounds
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
    
        # Draw game elements
        system_rendering(self.ecs_world, self.screen)
        
        # Draw title and instructions
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.instr1_text, self.instr1_rect)
        self.screen.blit(self.instr2_text, self.instr2_rect)
        self.screen.blit(self.instr3_text, self.instr3_rect)
        
        # Draw cooldown bar
        # Default colors
        bg_color = (100, 100, 100)
        ready_color = (50, 150, 255)
        cooldown_color = (255, 100, 100)
        
        # Use colors from interface.json if available
        if hasattr(self, 'interface_cfg') and 'cooldown' in self.interface_cfg:
            cooldown_cfg = self.interface_cfg['cooldown']
            bg_color = pygame.Color(
                cooldown_cfg['background_color'][0],
                cooldown_cfg['background_color'][1],
                cooldown_cfg['background_color'][2]
            )
            ready_color = pygame.Color(
                cooldown_cfg['ready_color'][0],
                cooldown_cfg['ready_color'][1],
                cooldown_cfg['ready_color'][2]
            )
            cooldown_color = pygame.Color(
                cooldown_cfg['cooldown_color'][0],
                cooldown_cfg['cooldown_color'][1],
                cooldown_cfg['cooldown_color'][2]
            )
        
        # Background
        pygame.draw.rect(
            self.screen,
            bg_color,
            (*self.cooldown_bar_position, self.cooldown_bar_width, self.cooldown_bar_height)
        )
        
        # Foreground
        if self.special_ability_ready:
            # Full bar if ready
            bar_color = ready_color
            bar_width = self.cooldown_bar_width
        else:
            # Partial bar if on cooldown
            bar_color = cooldown_color
            cooldown_percent = 1.0 - (self.special_ability_timer / self.special_ability_cooldown)
            bar_width = int(self.cooldown_bar_width * cooldown_percent)
        
        pygame.draw.rect(
            self.screen,
            bar_color,
            (self.cooldown_bar_position[0], self.cooldown_bar_position[1], bar_width, self.cooldown_bar_height)
        )
        
        # Label for the cooldown bar
        label_size = 12
        label_color = (255, 255, 255)
        
        if hasattr(self, 'interface_cfg') and 'cooldown' in self.interface_cfg:
            cooldown_cfg = self.interface_cfg['cooldown']
            label_size = cooldown_cfg['text_size']
            label_color = pygame.Color(
                cooldown_cfg['text_color'][0],
                cooldown_cfg['text_color'][1],
                cooldown_cfg['text_color'][2]
            )
        
        label_font = pygame.font.SysFont("Arial", label_size)
        label_text = "Special Ready!" if self.special_ability_ready else f"Cooldown: {self.special_ability_timer:.1f}s"
        label_surface = label_font.render(label_text, True, label_color)
        label_rect = label_surface.get_rect(midleft=(self.cooldown_bar_position[0] + self.cooldown_bar_width + 10, 
                                                self.cooldown_bar_position[1] + self.cooldown_bar_height // 2))
        self.screen.blit(label_surface, label_rect)
        
        # Draw pause text if paused
        if self.is_paused:
            # Add a semi-transparent overlay
            overlay = pygame.Surface((self.window_width, self.window_height))
            overlay.set_alpha(128)  # 50% transparent
            overlay.fill((0, 0, 0))  # Black overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw pause text over the overlay
            self.screen.blit(self.pause_text, self.pause_rect)
        
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()


    def _activate_special_ability(self):
        
        if not self.special_ability_ready:
            print("Special ability on cooldown!")
            return
        
        
        if self._player_entity is None or self._player_c_t is None or self._player_c_s is None:
            print("Player entity not fully initialized")
            return
        
        print("Special ability activated!")
        
        
        player_pos = self._player_c_t.pos
        center_x = player_pos.x + (self._player_c_s.area.width / 2)
        center_y = player_pos.y + (self._player_c_s.area.height / 2)
        player_center = pygame.Vector2(center_x, center_y)
        
        
        directions = [
            pygame.Vector2(0, -1),  # North
            pygame.Vector2(1, 0),   # East
            pygame.Vector2(0, 1),   # South
            pygame.Vector2(-1, 0)   # West
        ]
        
        
        for direction in directions:
            
            target_pos = player_center + direction * 1000  
            
            
            create_bullet(
                self.ecs_world,
                target_pos,
                player_center,
                self.bullet_cfg,
                self._player_c_s.area.size
            )
        
        
        self.special_ability_ready = False
        self.special_ability_timer = self.special_ability_cooldown
        
        
        if "special_sound" in self.bullet_cfg:
            ServiceLocator.sounds_service.play(self.bullet_cfg["special_sound"])
        else:
            
            ServiceLocator.sounds_service.play(self.bullet_cfg["sound"])

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