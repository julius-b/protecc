import pygame as pg
from const import *
from typing import Optional

# TODO add readable name
class InvItem():
    def __init__(self, code, tier, cnt, mods = []):
        self.code = code
        self.tier = tier
        self.mods = mods
        self.cnt = cnt
        pass

    # NOTE: doesn't include cnt
    def __eq__(self, other):
        if isinstance(other, InvItem):
            return self.code == other.code and self.tier == other.tier and self.mods == other.mods
        return False

# health, weapons, tools, armor?
# Applyable: usable on (.self = False), power up, mod tab on turret, eg. fire aspect
class Consumable():
    def __init__(self, health):
        self.health = healths

# turret, launcher, mine
class Placeable():
    def __init__(self):
        pass

class Inventory():
    width = 792
    height = 80
    screen_area = (WIDTH/2-width/2, HEIGHT-100)

    def __init__(self, game):
        self.game = game
        self.items: [Optional[InvItem]] = [None] * INVENTORY_SIZE
        self.pos = 0

    # TODO return where != None
    def __len__(self):
        return len(self.items)

    def select(self, pos):
        if pos >= 0 and pos < INVENTORY_SIZE:
            self.pos = pos

    def curr(self) -> Optional[InvItem]:
        return self.items[self.pos] if self.pos < len(self.items) else None

    def add(self, item) -> bool:
        empty = None
        for i, curr in enumerate(self.items):
            if curr == item:
                curr.cnt += item.cnt
                return True
            if curr == None and empty == None:
                empty = i
        if empty != None:
            self.items[empty] = item
            return True
        return False

    def remove_one(self, item):
        for i, curr in enumerate(self.items):
            if curr == item:
                curr.cnt -= 1
                if curr.cnt <= 0:
                    # NOTE: .remove relies on specific definition of eq (code, tier, mods)
                    self.items[i] = None
                break

    def click(self, abs_pos) -> bool:
        if abs_pos[0] > self.screen_area[0] and abs_pos[0] < self.screen_area[0]+self.width and abs_pos[1] > self.screen_area[1] and abs_pos[1] < self.screen_area[1]+self.height:
            offset = abs_pos[0] - self.screen_area[0]
            self.pos = int(offset // 88)

    def draw(self, surface):
        #pg.draw.rect(surface, DARKGREY, outline_rect, 2)
        # 80x80, 8 padding = 792
        # alt: rect at globally defined pos (just +offset), better for mouse collision (rects.collidepoint)
        inv_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        for i in range(INVENTORY_SIZE):
            rect = pg.Rect(i*88, 0, 80, 80)
            highlight = i == self.pos
            pg.draw.rect(inv_surface, 0xeaffffff if highlight else 0xd0ffffff, rect, border_radius=8)
            if i < len(self.items):
                if item := self.items[i]:
                    img = self.game.inv_images[item.code]
                    x = i*88 + 40 - img.width/2
                    y = 40 - img.height/2
                    inv_surface.blit(img, (x, y))
            if highlight:
                pg.draw.rect(inv_surface, 0xffadbce6, rect, width = 4, border_radius=8)
        surface.blit(inv_surface, self.screen_area)
