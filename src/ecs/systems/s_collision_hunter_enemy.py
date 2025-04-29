import esper
from src.create.prefab_creator import create_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_hunter import CTagHunter


def system_collision_hunter_enemy(world:esper.World, explosion_cfg:dict):
    componenets_hunters = world.get_components(CSurface, CTransform, CTagEnemy, CTagHunter)
    components_enemy = world.get_components(CSurface, CTransform, CTagEnemy)

    for hunter_entity, (c_surface_h, c_transform_h, _, _) in componenets_hunters:
        hunter_rect = CSurface.get_area_relative(c_surface_h.area, c_transform_h.pos)
        for enemy_entity, (c_surface_e, c_trasform_e, _) in components_enemy:
            enemy_rect = CSurface.get_area_relative(c_surface_e.area, c_trasform_e.pos)
            if(not(world.has_component(enemy_entity, CTagHunter)) and hunter_rect.colliderect(enemy_rect)):
                world.delete_entity(enemy_entity)
                world.delete_entity(hunter_entity)
                create_explosion(world, c_transform_h.pos, explosion_cfg)