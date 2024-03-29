from direct.showbase.DirectObject import DirectObject
from panda3d.core import BitMask32
from panda3d.core import Camera
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import CollisionSegment
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionTube
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import Point3
from panda3d.core import Vec3
from panda3d.core import Vec4
import math
from config import *

origin = Point3(0, 0, 0)

class TerrainCamera(Camera):
	def __init__(self):
		self.camNode = base.cam
		self.cam = self.camNode.node()
		self.cam.setTagStateKey('Normal')
		
class FollowCamera(TerrainCamera):
	def __init__(self, fulcrum, terrain):
		TerrainCamera.__init__(self)
		
		self.terrain = terrain
		self.fulcrum = fulcrum
		
		self.camNode.reparentTo(fulcrum)
		# How far should the camera be from character
		self.cameraDistance = 30
		# Initialize pitch of camera
		self.cameraPitch = 10
		self.focus = self.fulcrum.attachNewNode("focus")
		
		self.maxDistance = 500.0
		self.minDistance = 2
		self.maxPitch = 80
		self.minPitch = -70
		
		# We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
		self.cTrav = CollisionTraverser()
		self.cameraRay = CollisionSegment(self.fulcrum.getPos(), (0, 5, 5))
		self.cameraCol = CollisionNode('cameraRay')
		self.cameraCol.addSolid(self.cameraRay)
		self.cameraCol.setFromCollideMask(BitMask32.bit(0))
		self.cameraCol.setIntoCollideMask(BitMask32.allOff())
		self.cameraColNp = self.fulcrum.attachNewNode(self.cameraCol)
		self.cameraColHandler = CollisionHandlerQueue()
		self.cTrav.addCollider(self.cameraColNp, self.cameraColHandler)
		
	def zoom(self, zoomIn):
		if (zoomIn):
			self.cameraDistance += 0.1 * self.cameraDistance;
		else:
			self.cameraDistance -= 0.1 * self.cameraDistance;
		if self.cameraDistance < self.minDistance:
			self.cameraDistance = self.minDistance
		if self.cameraDistance > self.maxDistance:
			self.cameraDistance = self.maxDistance
			
	def update(self, x, y):
		# alter characters yaw by an amount proportionate to deltaX
		self.fulcrum.setH(self.fulcrum.getH() - 0.3 * x)
		# find the new camera pitch and clamp it to a reasonable range
		self.cameraPitch = self.cameraPitch + 0.1 * y
		if (self.cameraPitch < self.minPitch):
			self.cameraPitch = self.minPitch
		if (self.cameraPitch > self.maxPitch):
			self.cameraPitch = self.maxPitch
		self.cameraNode.setHpr(0, self.cameraPitch, 0)
		# set the camera at characters middle
		# should pivot around here instead of the view target which is noticeably higher
		self.camNode.setPos(0,0,0)
		# back the camera out to its proper distance
		self.camNode.setY(self.camNode, self.cameraDistance)
		self.fixHeight()
		correctedDistance = self.camNode.getPos().length()
		
		# point the camera at the view target
		forwardOffset = -math.sin(math.radians(self.cameraPitch))
		verticalOffset = 1 - math.sin(math.radians(self.cameraPitch))
		self.focus.setPos(0, forwardOffset, verticalOffset + correctedDistance / 8.0)
		# keep camera from flipping over
		if self.focus.getY() > self.camNode.getY() * 0.9:
			self.focus.setY(self.camNode.getY() * 0.9
		self.camNode.lookAt(self.focus)
		# reposition the end of the cameras obstruction ray trace
		self.cameraRay.setPointB(self.camNode.getPos())
		
	def fixHeight(self):
		pos = self.camNode.getPos(render)
		minz = self.terrain.getElevation(pos.x, pos.y) + 1.2
		if pos.z = minZ:
			pos.z = minZ
		self.camNode.setPos(render, pos)
	