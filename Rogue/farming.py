import libtcodpy as libtcod
 
#actual size of the window
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 90
 
#size of the map
MAP_WIDTH = 120
MAP_HEIGHT = 90

MAX_ROOM_MONSTERS = 50
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
 
color_dark_wall = libtcod.desaturated_red
color_dark_ground = libtcod.desaturated_yellow
 
 
class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
 
    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
 
    def draw(self):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_foreground_color(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
		
def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False
 
def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False
			
def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 25, MAX_ROOM_MONSTERS)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) < 30:  #80% chance of getting an orc
                #create an orc
                monster = Object(x, y, 'O', 'boulder', libtcod.dark_grey,
                    blocks=True)
            elif libtcod.random_get_int(0, 0, 100) < 30+30:  #80% chance of getting an orc
                #create a troll
                monster = Object(x, y, 'Y', 'tree', libtcod.darker_green,
                    blocks=True)
            elif libtcod.random_get_int(0, 0, 100) < 30+30+40:  #80% chance of getting an orc
                #create a troll
                monster = Object(x, y, 'o', 'stump', libtcod.dark_orange,
                    blocks=True)
 
            objects.append(monster)
 
def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def make_map():
    global map

    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
 
    #create two rooms
    room1 = Rect(0, 0, 119, 89)
    create_room(room1)
	
    #add some contents to this room, such as monsters
    place_objects(room1)

    create_v_tunnel(25, 21, 0) #22
    create_v_tunnel(68, 64, 119) #66
	
    #place the player inside the first room
    player.x = 25
    player.y = 23
 
 
def render_all():
    global color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
 
    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_back(con, x, y, color_dark_wall, libtcod.BKGND_SET )
            else:
                libtcod.console_set_back(con, x, y, color_dark_ground, libtcod.BKGND_SET )
 
    #draw all objects in the list
    for object in objects:
        object.draw()
 
    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
 
def handle_keys():
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
 
        #movement keys
		
    key_char = chr(key.c)
		
    if key_char == 'w':
        player.move(0, -1)
 
    elif key_char == 's':
        player.move(0, 1)
 
    elif key_char == 'a':
        player.move(-1, 0)
 
    elif key_char == 'd':
        player.move(1, 0)

 
#############################################
# Initialization & Main Loop
#############################################
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

#create object representing the player
player = Object(0, 0, 'H', 'player', libtcod.white, blocks=True)
 
#the list of objects starting with the player
objects = [player]
 
#generate map (at this point it's not drawn to the screen)
make_map()
 
while not libtcod.console_is_window_closed():
 
    #render the screen
    render_all()
 
    libtcod.console_flush()
 
    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()
 
    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break