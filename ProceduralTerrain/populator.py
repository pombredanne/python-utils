from terraintile import *
from direct.showbase.RandomNumGen import *
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3, Vec4, Point3, Point2
from pandac.PandaModules import Shader, Texture, TextureStage, TransparencyAttrib
from config import *

class LeafModel():
	def __init__(self, name, nrplates, width, height, shaderfile, texturefile, uvlist, jitter=-1):
		self.name = name
		self.texturefile = texturefile
		self.shaderfile = shaderfile
		
		self.np = NodePath('leaf')
		
		self.tex = loader.loadTexture('textures/' + texturefile)
		self.tex.setMinfilter(Texture.FTLinearMipmapLinear)
		self.tex.setMagfilter(Texture.FTLinearMipmapLinear)
		self.tex.setAnisotropDegree(2)
		self.np.setTexture(self.tex)
		self.np.setTwoSided(True)
		self.np.setTransparency(TransparencyAttrib.MAlpha)
		self.np.setDepthWrite(False)