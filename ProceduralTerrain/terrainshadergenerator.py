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
		self.textureMapper = textureMapper
		self.normalMapping = True
		self.detailTexture = True
		self.detailPnm = PNMImage()
		
		self.parallax = False
		self.glare = False
		self.avoidConditionals = 1
		self.fogExponential()
		logging.info("setting basic terrain shader input...")
		self.setDetail(self.texturer.detailTex)
		
		self.terrain.setShaderFloatInput("fogDensity", self.fogDensity)
		#self.terrain.setShaderFloatInput("fogDensity", 0)
		self.normalMapStrength = 1.6
		self.terrain.setShaderFloatInput("normalMapStrength", self.normalMapStrength)
		self.parallaxStrength = 0.01
		self.terrain.setShaderFloatInput("parallaxStrength", self.parallaxStrength)
		
		self.debugDisableDiffuse = 0
		self.terrain.setShaderFloatInput("debugDisableDiffuse", self.debugDisableDiffuse)
		
		self.detailHugeScale = self.terrain.tileSize / 50 * TERRAIN_HORIZONTAL_STRETCH
		self.detailBigScale = self.terrain.tileSize / 9 * TERRAIN_HORIZONTAL_STRETCH
		self.detailSmallScale = self.terrain.tileSize / 2.2 * TERRAIN_HORIZONTAL_STRETCH
		self.terrain.setShaderFloatInput("detailHugeScale", self.detailHugeScale)
		self.terrain.setShaderFloatInput("detailBigScale", self.detailBigScale)
		self.terrain.setShaderFloatInput("detailSmallScale", self.detailSmallScale)
		
		self.terrain.setShaderFloatInput("ambientOcclusion", 1.0)
		logging.info("done")
		
	def setDetail(self, texture):	
		texture.store(self.detailPnm)
		# compensate for darkness of detail texture
		self.detailBrightnessCompensation = 1.0 / self.detailPnm.getAverageGray()
		# 3 layers of detail texture actually
		self.detailBrightnessCompensation *= self.detailBrightnessCompensation * self.detailBrightnessCompensation
		self.terrain.setShaderInput("detailTex", texture)
		self.terrain.setShaderFloatInput("brightnessAdjust", self.detailBrightnessCompensation)
		
	def addTexture(self, texture):
		self.textureMapper.addTexture(texture)
		
	def addRegionToText(self, region, textureNumber=-1):
		self.textureMapper.addRegionToTex(region, textureNumber)
		
	def fogLinear(self):
		# We need to figure out what fog density we want.
		# Lets find out what density results in 80% fog at max view distance
		
		self.fogDensity = 0.8 * (self.terrain.maxViewRange)
		self.fogFunction = '''
float FogAmount( float maxDistance, float3 PositionVS )
{
	float z = length( PositionVS ); // viewer position is at origin
	return saturate( 1-(z / maxDistance));
}'''

	def fogExponential(self):
		# We need to figure out what fog density we want.
        # Lets find out what density results in 75% fog at max view distance
        # the basic fog equation...
        # fog = e^ (-density * z)
        # -density * z = ln(fog) / ln(e)
        # -density * z = ln(fog)
        # density = ln(fog) / -z
        # density = ln(0.25) / -maxViewRange
		self.fogDensity = 1.38629436 / (self.terrain.maxViewRange + 30)
		self.fogFunction = '''
float FogAmount( float density, float3 PositionVS )
{
	float z = length( PositionVS ); // viewer position is at origin
	return saturate( pow(2.7182818, -(density * z)));
}'''

	def fogExponential2(self):
		# We need to figure out what fog density we want.
        # Lets find out what density results in 80% fog at max view distance
        # the basic fog equation...
        #
        # fog = e^ (-density * z)*(-density * z)
        # -density^2 * z^2 = ln(fog) / ln(e)
        # -density^2 * z^2 = ln(fog)
        # density = root(ln(fog) / -z^2)
        # density = root(ln(0.2) / -maxViewRange * maxViewRange)
		self.fogDensity = 1.60943791 / (self.terrain.maxViewRange * self.terrain.maxViewRange)
		self.fogFunction = '''
float FogAmount( float density, float3 PositionVS )
{
	float z = length( PositionVS ); // viewer position is at origin
	float exp = density * z;
	return saturate( pow(2.7182818, -(exp * exp)));
}'''

	def getHeader(self):
		
		header = '''
//Cg
//
//Cg profile arbvp1 arbfp1
// Should use per-pixel lighting, hdr1, and medium bloom
// input alight0, dlight0

'''
		header += 'const float slopeScale = '
		header += str(self.terrain.maxHeight / self.terrain.horizontalScale) + ';'
		return header
		
		
	def getFunctions(self):
		function = ''
		if self.fogDensity:
			functions += '''
//returns [0,1] fog factor
'''
			functions += self.fogFunction
		functions += '''
		
float3 absoluteValue(float3 input)
{
	return float3(abs(input.x), abs(input.y), abs(input.z));
}
'''