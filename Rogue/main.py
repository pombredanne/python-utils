import libtcodpy as libtcod
import math
import textwrap
import shelve

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

FOV_ALGO = 0 #default FOV algorithm
FOV_LIGHT_WALLS = True #ligh walls or not
TORCH_RADIUS = 10

LIMIT_FPS = 20 #20 frames per second maximum

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

class Tile:
	#a tile of the map and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		
		#all tiles start unexplored
		self.explored = False
		
		#by default, if a tile is blocked it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight
		
class Rect:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
		
	def center(self):
		center_x = (self.x1 + self.x2) / 2
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)
		
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)
				
class Object:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.color = color
		self.blocks = blocks
		self.always_visible = always_visible
		self.fighter = fighter
		if self.fighter: #let the fighter component know who owns it
			self.fighter.owner = self
			
		self.ai = ai
		if self.ai: #let the AI component know who owns it
			self.ai.owner = self
			
		self.item = item
		if self.item: #let the Item component know who owns it
			self.item.owner = self
			
		self.equipment = equipment
		if self.equipment: #let the Equipment component know who owns it
			self.equipment.owner = self
			
			#there must be an Item component for the Equipment component to work properly
			self.item = Item()
			self.item.owner = self
			
	def move(self, dx, dy):
		#move by the given amount, if the destination is not blocked
		if not is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
			
	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)
		
		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)
		
	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)
		
	def distance(self, x, y):
		#return the distance to some coordinates
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
		
	def send_to_back(self):
		#make this object be drawn first, so all others appear above it if they're in the same tile.
		global objects
		objects.remove(self)
		objects.insert(0, self)
		
	def draw(self):
		#only show if it's visible to the player; or it's set to "always visible" and on an explored tile
		if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
			(self.always_visible and map[self.x][self.y].explored)):
			#set the color and then draw the character that represents this object at its position
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
			
	def clear(self):
		#erase the character that represents this object
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

		
class Fighter:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, defense, power, xp, death_function=None):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defense = defense
		self.base_power = power
		self.xp = xp
		self.death_function = death_function
		
	@property
	def power(self):  #return actual power, by summing up the bonuses from all equipped items
		bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
		return self.base_power + bonus