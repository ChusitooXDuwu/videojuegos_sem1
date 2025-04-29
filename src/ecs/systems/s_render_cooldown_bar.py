
import esper
import pygame
from src.ecs.components.c_special_ability import CSpecialAbility
from src.ecs.components.tags.c_tag_player import CTagPlayer

def system_render_cooldown_bar(world: esper.World, screen: pygame.Surface):
    """System that renders the cooldown bar for special abilities"""
    components = world.get_components(CSpecialAbility, CTagPlayer)
    
    for _, (special_ability, _) in components:
        # Configuration
        bar_width = 100
        bar_height = 15
        bar_position = (20, screen.get_height() - 25)  # Bottom left
        
       
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            (*bar_position, bar_width, bar_height)
        )
        
      
        if special_ability.is_ready:
           
            bar_color = (50, 150, 255)
            filled_width = bar_width
        else:
            
            bar_color = (255, 100, 100)
            cooldown_percent = 1.0 - (special_ability.current_cooldown / special_ability.cooldown_time)
            filled_width = int(bar_width * cooldown_percent)
        
        pygame.draw.rect(
            screen,
            bar_color,
            (bar_position[0], bar_position[1], filled_width, bar_height)
        )
        
        
        label_font = pygame.font.SysFont("Arial", 12)
        if special_ability.is_ready:
            label_text = "Special Ready!"
        else:
            label_text = f"Cooldown: {special_ability.current_cooldown:.1f}s"
            
        label_surface = label_font.render(label_text, True, (255, 255, 255))
        label_rect = label_surface.get_rect(
            midleft=(bar_position[0] + bar_width + 10, bar_position[1] + bar_height // 2)
        )
        screen.blit(label_surface, label_rect)