import pygame as pg
vec = pg.math.Vector2

# stats
class WeaponSpec():
    def __init__(self, fire_rate, dmg, spread, p_speed, p_lifetime, p_size, p_count = 1, recoil = 0):
        self.fire_rate = fire_rate
        self.dmg = dmg
        self.spread = spread
        self.recoil = recoil
        self.p_count = p_count
        self.p_speed = p_speed
        self.p_lifetime = p_lifetime
        self.p_size = p_size

class ConsumableSpec():
    def __init__(self, health):
        self.health = health

class MineSpec():
    def __init__(self, dmg):
        self.dmg = dmg

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40) # 35
LIGHTGREY = (100, 100, 100)
LIGHTWHITE = (200, 200, 200, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# Game settings
WIDTH = 1408  # 64 * 22
HEIGHT = 960  # 64 * 15
FPS = 60
TITLE = "Protecc!"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)
INVENTORY_SIZE = 9
PLAYER_IMGS = ['char/manBlue_hold.png', 'char/manBlue_gun.png', 'char/manBlue_machine.png']
PEER_IMGS = ['char/survivor1_hold.png', 'char/survivor1_gun.png', 'char/survivor1_machine.png']
CHAR_ITEM_MAP = {
    'pistol': 'gun',
    'shotgun': 'machine',
    'rifle': 'machine'
}

# Item settings
BULLET_IMG = 'bullet.png'
WEAPONS: dict[str, [WeaponSpec]] = {}
WEAPONS['pistol'] = [
        WeaponSpec(
                fire_rate = 450,
                dmg = 10,
                spread = 6,
                recoil = 230,
                p_speed = 500,
                p_lifetime = 800,
                p_size = 'lg'
        ),
        WeaponSpec(
                fire_rate = 300,
                dmg = 11,
                spread = 5,
                recoil = 200,
                p_speed = 550,
                p_lifetime = 1000,
                p_size = 'lg'
        ),
        # TODO ensure tier1 rifle < this < tier2 rifle!
        # ensure spread always higher than rifle? speed lower
        WeaponSpec(
                fire_rate = 220,
                dmg = 12,
                spread = 4,
                recoil = 180,
                p_speed = 600,
                p_lifetime = 1200,
                p_size = 'lg'
        )
]
# TODO add lots of stopping power to shotguns
WEAPONS['shotgun'] = [
        WeaponSpec(
                fire_rate = 950,
                dmg = 4,
                spread = 22,
                recoil = 320,
                p_speed = 400,
                p_lifetime = 480,
                p_size = 'sm',
                p_count = 12,
        )
]
WEAPONS['rifle'] = [
        WeaponSpec(
                fire_rate = 200,
                dmg = 13,
                spread = 4,
                # consider how often it is applied
                recoil = 180,
                p_speed = 620,
                p_lifetime = 1300,
                p_size = 'lg'
        )
]

PLACEABLES = {}
# turrets
PLACEABLES['callisto'] = [
        WeaponSpec(
                fire_rate = 200,
                dmg = 14,
                spread = 3,
                p_speed = 650,
                # TODO size..... to draw a radius would depend on speed... -- TODO calculate radius like that :)
                p_lifetime = 1300,
                # TODO medium?
                p_size = 'lg'
        )
]

# launchers
PLACEABLES['cerberus'] = []

# mines
MINES: dict[str, [MineSpec]] = {}
MINES['boom'] = [
    MineSpec(200)
]

CONSUMABLES: dict[str, [ConsumableSpec]] = {}
CONSUMABLES['health'] = [
    ConsumableSpec(health = 20)
]

# TODO dup
MINE_IMG = 'spaceBuilding_009.png'
TURRET_BASE_IMG = 'turret/tile_0016.png'
TURRET_TOP_IMGS = ['turret/tile_0018.png', 'turret/tile_0017.png']
TURRET_OFFSET = vec(0, 25)

# silo
LAUNCHER_IMG = 'turret/ufoBlue.png'

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
BOOM = ['boom/explosion1.png', 'boom/explosion2.png', 'boom/explosion3.png',
        'boom/explosion4.png', 'boom/explosion5.png']
SPLAT = 'splat green.png'
FLASH_DURATION = 50
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {
    'health': 'item/tile_0024.png',
    'pow': 'item/tile_0025.png',
    'pistol': 'item/tile_0011.png',
    'shotgun': 'item/tile_0017.png',
    'rifle': 'item/tile_0015.png',
    # NOTE: dup - TODO different minelayer img?
    'boom': 'spaceBuilding_009.png'
}
BOB_RANGE = 10
BOB_SPEED = 0.3

# Sounds
BG_MUSIC = '.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                 'shotgun': ['shotgun.wav'],
                 'rifle': ['pistol.wav']}
EFFECTS_SOUNDS = {#'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}
BOOM_SOUNDS = ['boom1.wav', 'boom2.wav']

PLAYER_PACKET = '!cBfffB'
MSG_PLAYER = b'p'
