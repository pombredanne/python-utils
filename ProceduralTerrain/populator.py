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
		
		maker = CardMaker('leaf')
		maker.setFrame(-width/2.0, width/2.0, 0, height)
		#maker.setFrame(0,1,0,1)
		for i in range(nrplates):
			if uvlist != None:
				maker.setUvRange(uvlist[i][0], uvlist[i][1])
			else:
				maker.setUvRange(Point2(0,0), Point2(1,0.98))
			node = self.np.attachNewNode(maker.generate())
			#node.setTwoSided(True)
			node.setHpr(i * 180.0 / nrplates,0,0)
		self.np.flattenStrong()
		#np.flattenLight()
		#np.setTwoSided(True)
		
		if jitter == -1:
			self.jitter = height/width/2
		else:
			self.jitter = jitter
			
copy = NodePath()

tree = LeafModel("Tree 1", 3, 5.0, 5.0, None, 'Bleech.png', None)

def makeTree():
	np = tree.np.copyTo(copy)
	#np = self.model.instanceTo(self.grassNP)
	#np = loader.loadModel('models/grass.egg')
	#np.reparentTo(self.grassNP)
	#np.setTwoSided(True)
	#np.setHpr(Vec3(heading, 0, 0))
	#np.setPos(pos)
	#logging.info(np)
	return np
	
sphere = loader.loadModel("models/sphere")

def makeSphere():
	np = NodePath()
	sphere.copyTo(np)