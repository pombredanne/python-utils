"""
terrain.py: This file contains the terrain engine for panda 3d.

The TerrainTile is a customized version of Panda3d's GeoMipTerrain.

The HeightMap coverts world x,y coordinates into terrain height and is
therefore responsible for the appearance of terrain geometry.

The TerrainTexturer handles all textures and or shaders on the terrain and is
generally responsible for the appearance of the terrain.

The Terrain class ties all of these elements together. It is responsible for
tiling together the terrain tiles and storing their common attributes.
"""
__author__ = "Stephen Lujan"
__date__ = "$Oct 27, 2010 4:47:05 AM$"

import math

from collections import deque
from config import *
from direct.showbase.RandomNumGen import *
from direct.task.Task import Task
from panda3d.core import BitMask32
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import CollisionTraverser
from panda3d.core import PNMImage
from panda3d.core import PerlinNoise2
from panda3d.core import StackedPerlinNoise2
from panda3d.core import TimeVal
from pandac.PandaModules import NodePath
from pandac.PandaModules import PTAFloat
from pandac.PandaModules import SceneGraphReducer
from populator import *
from pstat_debug import pstat
from terraintexturer import *
from terraintile import *

"""
    Panda3d GeoMipTerrain tips:
least detail = max detail level = log(block_size) / log(2)
most detail = min detail level = 0
Block size does not effect the detail level. It only limits the max detail level.
Each block in a GeoMipTerrain can set its own detail level on update if
bruteforce is disabled.

    Performance Note:
In creating new tiles GeoMipTerrain.generate() is the biggest performance hit,
taking up about 5/7 of the time spent in Terrain._generateTile().
Most of the remainder is spent in Terrain.getHeight(). Everything else involved
in adding and removing tiles is trivial in practice.
"""


###############################################################################
#   HeightMap
###############################################################################

class HeightMap():
	"""HeightMap functionally maps any x and y to the appropriate height for realistic terrain."""
	
	def __init__(self, id, flatHeight=0.3):
		
		self.id = id
		# the overall smoothness/roughness of the terrain
		self.smoothness = 150
		# now quickly altitude and roughness shift
		self.consistency = self.smoothness * 12
		# for realism the flatHeight should be at or very close to waterHeight
		self.flatHeight = flatHeight
		#creates noise objects that will be used by the getHeight function
		self.generateNoiseObjects()
		self.normalize()
		
	def normalize(self):
		#normalize the range of possible heights to be bounded [0,1]
		minmax = []
		for x in range(2):
			for y in range(2):
				minmax.append(self.getPrenormalizedHeight(x, y))
		min = 9999
		max = -9999
		for x in minmax:
			if x < min:
				min = x
			if x > max:
				max = x
		self.normalizerSub = min
		self.normalizerMult = 1.0 / (max-min)
		
		logging.info("height normalized from [" + str(min) + "," + str(max) + "]")
		
	def generateStackedPerlin(self, perlin, frequency, layers, frequencySpread, amplitudeSpread, id):
		
		for x in range(layers):
			layer = PerlinNoise2(0, 0, 256, seed=id + x)
			layer.setScale(frequency / (math.pow(frequencySpread, x)))
			perlin.addLevel(layer, 1 / (math.pow(amplitudeSpread, x)))
			
	def generateNoiseObjects(self):
		"""Create perlin noise."""
		
		# See getHeight() for more details....
        # where perlin 1 is low terrain will be mostly low and flat
        # where it is high terrain will be higher and slopes will be exagerrated
        # increase perlin1 to create larger areas of geographic consistency
		self.perlin1 = StackedPerlinNoise2()
		self.generateStackedPerlin(self.perlin1, self.consistency, 4, 2, 2.5, self.id)
		
		# perlin2 creates the noticeable noise in the terrain
        # without perlin2 everything would look unnaturally smooth and regular
        # increase perlin2 to make the terrain smoother
		self.perlin2 = StackedPerlinNoise2()
		self.generateStackedPerlin(self.perlin2, self.smoothness, 8, 2, 2.2, self.id + 100)
		
	def getPrenormalizedHeight(self, p1, p2):
		"""Returns the height at the specified terrain coordinates.
		
		The input is a value from each of the noise functions
		
		"""
		
		fh = self.flatHeight
		# p1 varies what kind of terrain is in the area, p1 alone would be smooth
        # p2 introduces the visible noise and roughness
        # when p1 is high the altitude will be high overall
        # when p1 is close to fh most of the visible noise will be muted
		return (p1 - fh + (p1 - fh) * (p2 - fh)) / 2 + fh
		# if p1 = fh, the whole equation simplifies to...
        # 1. (fh - fh + (fh - fh) * (p2 - fh)) / 2 + fh
        # 2. ( 0 + 0 * (p2 - fh)) / 2 + fh
        # 3. (0 + 0 ) / 2 + fh
        # 4. fh
        # The important part to understanding the equation is at step 2.
        # The closer p1 is to fh, the smaller the mutiplier for p2 becomes.
        # As p2 diminishes, so does the roughness.
		
	#@pstat
	def getHeight(self, x, y):
		"""Returns the height at the specified terrain coordinates.
		
		The values returned should be between 0 and 1 and use the full range.
		Heights should be the smoothest and flatest at flatHeight.
		
		"""
		p1 = (self.perlin1(x, y) + 1) / 2 # low frequency
		p2 = (self.perlin2(x, y) + 1) / 2 # high frequency
		
		return (self.getPrenormalizedHeight(p1, p2)-self.normalizerSub) * self.normalizerMult
		
###############################################################################
#   Terrain
###############################################################################

class Terrain(NodePath):
	"""A terrain contains a set of geomipmaps, and maintains their common properties."""
	
	def __init__(self, name, focus, maxRange, populator=None, feedBackString=None, id=0):
		"""Create a new terrain centered on the focus.
		
		The focus is the NodePath where the LOD is the greatest.
		id is a seed for the map and unique name for any cached heightmap images
		
		"""
		
		NodePath.__init__(self, name)
		
		### Basic Parameters
		self.name = name
		# nodepath to center of the level of detail
		self.focus = focus
		# stores all terrain tiles that make up the terrain
		self.tiles = {}
		# stores previously built tiles we can readd to the terrain
		self.storage = {}
		self.feedBackString = feedBackString
		if populator == None:
			populator = TerrainPopulator()
		self.populator = populator
		
		self.graphReducer = SceneGraphReducer()
		
		if THREAD_LOAD_TERRAIN:
			self.tileBuilder = TerrainTileBuilder(self)
			
		##### Terrain Tile physical properties
		self.maxHeight = MAX_TERRAIN_HEIGHT
		self.tileSize = 128
		self.heightMapSize = self.tileSize + 1
		
		##### Terrain scale and tile distances
		# distances are measured in tile's smallest unit
		# conversion to world units may be necessary
		# Don't show untiled terrain below this distance etc.
		# scale the terrain vertically to its maximum height
		self.setSz(self.maxHeight)
		# scale horizontally to appearance/performance balance
		self.horizontalScale = TERRAIN_HORIZONTAL_STRETCH
		self.setSx(self.horizontalScale)
		self.setSy(self.horizontalScale)
		# waterHeight is expressed as a multiplier to the max height
		self.waterHeight = 0.3
		
		#this is the furthest the camera can view
		self.maxViewRange = maxRange
		# Add half the tile size because distance is checked from the center,
		# not from the closest edge.
		self.minTileDistance = self.maxViewRange / self.horizontalScale + self.tileSize / 2
		# to avoid excessive store / retrieve behavior on tiles we have a small
		# buffer where it doesn't matter whether or not the tile is present
		self.maxTileDistance = self.minTileDistance + self.tileSize / 2
		
		##### heightmap properties
		self.initializeHeightMap(id)
		
		##### rendering properties
		self.initializeRenderProperties()