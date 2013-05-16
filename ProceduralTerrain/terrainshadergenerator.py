"""
terrainshadergenerator.py: This file contains a shader generator
specific to the terrain in this engine.
"""
__author__ = "Stephen Lujan"

from config import *
from panda3d.core import Shader
from pandac.PandaModules import PTAFloat
from terraintexturemap import *

###############################################################################
#   TerrainShaderGenerator
###############################################################################

class TerrainShaderGenerator:

	def __init__(self, terrain, texturer, textureMapper=None):
		
		self.terrain = terrain
		self.texturer = texturer
		if not textureMapper:
			textureMapper = TextureMapper(terrain)