from direct.task import Task
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import CollisionRay, CollisionNode, GeomNode, CollisionTraverser
from panda3d.core import CollisionHandlerQueue, CollisionSphere, BitMask32
from terrain import *

class MapEditor():
	def __init__(self, terrain):
		self.terrain = terrain
		self.terrain.setTag('EditableTerrain', '1')
		self.cursor = render.attachNewNode('EditCursor')
		loader.loadModel("models/sphere").reparentTo(self.cursor)
		self.size = 10.0
		self.cursor.setScale(self.size)
		self.cursor.setRenderModeWireframe()
		self.setupMouseCollision()
		self.on = False
		self.disable()
		
	def enable(self):
		taskMgr.add(self.update, "terrainEditor")
		self.cursor.unstash()
		
	def disable(self):
		taskMgr.remove("terrainEditor")
		self.cursor.stash()
		
	def toggle(self, value = None):
		if value == None:
			self.on = not self.on
		else:
			self.on = value
		if self.on:
			self.enable()
		else:
			self.disable()
			
	def update(self, task):
		self.onMouseTask()
		return Task.cont
		
	def onMouseTask(self):
		""" """
		# do we have a mouse
		logging.info("onMouseTask")
		if (base.mouseWatcherNode.hasMouse() == False):
			logging.error("no mouse")
			return
			
		# get the mouse position
		mpos = base.mouseWatcherNode.getMouse()
		
		# Set the position of the ray based on the mouse position
		if not self.mPickRay.setFromLens(base.camNode, mpos.getX(), mpos.getY()):
			logging.error("point is not acceptable")