import pygame as pg
from random import uniform, choice, randint, random
from const import *
from util import *
from items import *
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

# TODO debug draw both radii
# explosion radius wider than detection radius, otherwise only one mob at a time is hit
# TODO crater?
class Mine(pg.sprite.Sprite):
    def __init__(self, game, pos, owner):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.mines, game.placeables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mine_img
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.owner = owner
        self.boom = False
        # TODO radius dmg falloff, linear or sqrt?
        self.dmg = 200
        self.radius = 45
        self.boom_radius = self.radius*3

    def update(self):
        if not self.boom:
            return

        hits = pg.sprite.spritecollide(self, self.game.mines, False, boom_collision)
        for hit in hits:
            # NOTE: arbitrary whether self or hit runs update first, maybe set a number of how many ms to wait...
            hit.boom = True

        hits = pg.sprite.spritecollide(self, self.game.mobs, False, boom_collision)
        for hit in hits:
            hit.health -= self.dmg

        snd = self.game.boom_sounds[1] #choice(self.game.boom_sounds)
        if snd.get_num_channels() > 2:
            snd.stop()
        snd.play()
        Boom(self.game, self.rect.center, self.dmg-10)
        self.kill()

class Missile(pg.sprite.Sprite):
    def __init__(self):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.missiles
        pg.sprite.Sprite.__init__(self, self.groups)

class Turret(pg.sprite.Sprite):
    def __init__(self, game, pos, owner, tier = 0):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.turrets, game.placeables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = Turret.base_img(game, tier)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.tier = tier
        self.owner = owner
        self.pos = vec(pos)
        self.last_shot = 0
        self.dmg = 200
        self.radius = 45
        self.target = None
        self.rot = 0

    def shoot(self):
        weapon = PLACEABLES['callisto'][0]
        now = pg.time.get_ticks()
        if now - self.last_shot > weapon.fire_rate:
            self.last_shot = now
            dir = vec(0, 1).rotate(-self.rot)
            pos = self.pos + TURRET_OFFSET.rotate(-self.rot)
            for i in range(weapon.p_count):
                spread = uniform(-weapon.spread, weapon.spread)
                Projectile(self.game, pos, dir.rotate(spread), weapon)
                #snd = choice(self.game.weapon_sounds[item.code])
                #if snd.get_num_channels() > 2:
                #    snd.stop()
                #snd.play()
            MuzzleFlash(self.game, pos)

    def update(self):
        # TODO find nearest mob
        # TODO check if self.target alive & in range
        if self.target:
            if not self.target[0].alive():
                self.target = None
            else:
                target_vec = self.target[0].pos - self.pos
                dist = target_vec.length_squared()
                if dist < DETECT_RADIUS**2:
                    self.target = (self.target[0], target_vec, dist)
                else:
                    self.target = None
        if not self.target:
            for mob in self.game.mobs:
                target_vec = mob.pos - self.pos
                dist = target_vec.length_squared()
                if dist < DETECT_RADIUS**2 and (not self.target or self.target[2] > dist):
                    self.target = (mob, target_vec, dist)
        if self.target:
            self.rot = self.target[1].angle_to(vec(0, 1))
            image = self.game.turret_base_img.copy()
            top_img = self.game.turret_top_imgs[self.tier]
            top_img_rot = pg.transform.rotate(top_img, self.rot)
            new_rect = top_img_rot.get_rect(center = top_img.get_rect(center = (image.width/2, image.height/2)).center)
            image.blit(top_img_rot, new_rect)
            self.image = image
            #self.rot = target_vec.angle_to(vec(0, 1))
            #image = self.game.turret_base_img.copy()
            #top_img = pg.transform.rotate(self.game.turret_top_imgs[self.tier], self.rot)
            #image.blit(top_img, (image.width/2 - top_img.width/2, image.height/2 - top_img.height/2))
            #self.image = image
            self.shoot()

    def base_img(game, tier):
        image = game.turret_base_img.copy()
        image.blit(game.turret_top_imgs[tier], (game.turret_base_img.width/2-game.turret_top_imgs[tier].width/2, game.turret_base_img.height/2-game.turret_top_imgs[tier].height/2))
        return image

class Peer(pg.sprite.Sprite):
    def __init__(self, game, x, y, rot, health):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.peers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # TODO
        self.image = game.peer_img['gun']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.rot = rot
        self.health = health

    def apply(self, x, y, rot, health):
        self.rect.center = (x, y)
        self.rot = rot
        self.health = health
        self.image = pg.transform.rotate(self.game.peer_img, self.rot)

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.inventory = game.inventory
        self.img = game.player_imgs['hold']
        self.image = self.img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.damaged = False

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            # shoot via mouse, keep (for notebook)
            item = self.inventory.curr()
            if item == None:
                return
            if item.code in WEAPONS:
                self.shoot(item)
            # TODO consumable should only trigger on KEYDOWN
            elif item.code in CONSUMABLES:
                self.consume(item)
            elif item.code in PLACEABLES:
                self.place(item)
            elif item.code in MINES:
                self.place_mine(item)

    def consume(self, item):
        consumable = CONSUMABLES[item.code][item.tier]
        if self.health != PLAYER_HEALTH:
            self.add_health(consumable.health)
            self.inventory.remove_one(item)
            self.game.effects_sounds['health_up'].play()

    # TODO check ammo
    def shoot(self, item):
        weapon = WEAPONS[item.code][item.tier]
        now = pg.time.get_ticks()
        if now - self.last_shot > weapon.fire_rate:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            self.vel = vec(-weapon.recoil, 0).rotate(-self.rot)
            for i in range(weapon.p_count):
                spread = uniform(-weapon.spread, weapon.spread)
                Projectile(self.game, pos, dir.rotate(spread), weapon)
                snd = choice(self.game.weapon_sounds[item.code])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzleFlash(self.game, pos)

    # TODO mouse!
    def place_mine(self, item):
        # TODO distance to closest mine has to be at least radius*2.5
        for p in self.game.placeables:
            if (self.pos - p.rect.center).length_squared() <= (25*2)**2:
                return
        Mine(self.game, self.pos, True)

    def place(self, item):
        for p in self.game.placeables:
            if (self.pos - p.rect.center).length_squared() <= (40*1.5)**2:
                return
        Turret(self.game, self.pos, True)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        self.get_keys()
        # TODO
        item = self.inventory.curr()
        item = item.code if item else None
        if item in CHAR_ITEM_MAP:
            self.img = self.game.player_imgs[CHAR_ITEM_MAP[item]]
        else:
            self.img = self.game.player_imgs['hold']
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_vec = self.target.pos - self.pos
        if target_vec.length_squared() < DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_vec.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            # ValueError: Cannot scale a vector with zero length
            if self.acc.length_squared() > 0: # != 0.0
                print(self.acc) # TODO still not fixed
                self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Projectile(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, weapon: WeaponSpec):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[weapon.p_size]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir * weapon.p_speed * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.dmg = weapon.dmg
        self.lifetime = weapon.p_lifetime

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Boom(pg.sprite.Sprite):
    def __init__(self, game, pos, size):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = size
        self.image = pg.transform.scale(self.game.boom[0], (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        frame = (pg.time.get_ticks() - self.spawn_time) // 60
        if len(self.game.boom) > frame:
            self.image = pg.transform.scale(self.game.boom[frame], (self.size, self.size))
        else:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, code):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[code]
        self.rect = self.image.get_rect()
        self.item = InvItem(code, 0, 0) # TODO take from arg: file / generated pickup, etc.
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
