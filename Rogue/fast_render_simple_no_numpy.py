
import libtcodpy as libtcod
import os
import math


#size of the screen, in tiles
SCREEN_W = 80
SCREEN_H = 50
HALF_W = SCREEN_W / 2
HALF_H = SCREEN_H / 2


#initialize libtcod
libtcod.console_set_custom_font(os.path.join('data','fonts','arial10x10.png'),
	libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_W, SCREEN_H, 'libtcod sample', False)

#lists of background RGB values of all tiles
R = [0] * SCREEN_W * SCREEN_H
G = [0] * SCREEN_W * SCREEN_H
B = [0] * SCREEN_W * SCREEN_H

t = 0

while not libtcod.console_is_window_closed():
	#escape key to exit
	key = libtcod.console_check_for_keypress()
	if key.vk == libtcod.KEY_ESCAPE: break
	
	#move the light around in a circle
	t += 0.02
	lightx = HALF_W + HALF_H * math.cos(t)
	lighty = HALF_H + HALF_H * math.sin(t)
	
	for x in range(SCREEN_W):
		for y in range(SCREEN_H):
			#define the brightness of a light in a tile as the inverse of the
			#squared distance from that tile to the light.
			sqr_distance = (x - lightx)**2 + (y - lighty)**2
			brightness = 5.0 / sqr_distance
			
			#convert to 0-255 range
			brightness = int(brightness * 255)
			#truncate values outside that range
			brightness = max(min(brightness, 255), 0)
			
			#make a blue light by only setting the blue component and leaving others at 0
			B[SCREEN_W * y + x] = brightness
	
	#fill the screen with these background colors
	libtcod.console_fill_background(0, R, G, B)
	
	#show FPS
	libtcod.console_set_foreground_color(0, libtcod.white)
	libtcod.console_print_right(None, SCREEN_W-1, SCREEN_H-1,
		libtcod.BKGND_SET, '%3d FPS' % libtcod.sys_get_fps())
	
	libtcod.console_flush()

