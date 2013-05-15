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