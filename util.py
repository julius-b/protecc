import pygame as pg
vec = pg.math.Vector2

# TODO: pygame.sprite.collide_circle() seems to be different?
def radius_collision(left, right):
    if left != right:
        # NOTE: explosion only hurts if it engulfs an entity past the centre?
        # draw explosion at slightly smaller radius so it seems as though entities only touched slightly by this radius are not affected at all
        # or draw at full radius and it's possible to get 'burnt' without taking dmg
        distance = vec(left.rect.center).distance_squared_to(right.rect.center)
        return distance < left.radius**2
    else:
        return False

def boom_collision(left, right):
    if left != right:
        # NOTE: explosion only hurts if it engulfs an entity past the centre?
        # draw explosion at slightly smaller radius so it seems as though entities only touched slightly by this radius are not affected at all
        # or draw at full radius and it's possible to get 'burnt' without taking dmg
        distance = vec(left.rect.center).distance_squared_to(right.rect.center)
        return distance < left.boom_radius**2
    else:
        return False
