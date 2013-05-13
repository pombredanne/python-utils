import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import Vec3, Vec4, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

from panda3d.ai import *

SPEED = 0.5

MYDIR = os.path.abspath(sys.path[0])
MYDIR = Filename.fromOsSpecific(MYDIR).getFullpath()

font = loader.loadFont("cmss12")

def addInstructions(pos, msg):
	return OnscreenText(text=msg, style=1, fg=(1,1,1,1), font=font, pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)
	
def addTitle(text):
	return OnscreenText(text=text, style=1, fg=(1,1,1,1), font=font, pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)
	
class World(DirectObject):
	def __init__(self):
		self.switchState = True
		self.switchCam = False
		self.path_no = 1
		self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
		base.win.setClearColor(Vec4(0,0,0,1))
		base.cam.setPosHpr(17.79,-87.64,90.16,38.66,325.36,0)
		
		self.title = addTitle("Roaming Ralph (Walking on Uneven Terrain)")
		self.inst1 = addInstructions(0.95, "[ESC]: Quit")
		self.inst2 = addInstructions(0.90, "[Space - do Only once]: Start Pathfinding")
		self.inst3 = addInstructions(0.85, "[Enter]: Change camera view")
		
		self.environ = loader.loadModel("models/world")
		self.environ.reparentTo(render)
		self.environ.setPos(12,0,0)
		
		self.box = loader.loadModel("models/box")
		self.box.reparentTo(render)
		self.box.setPos(-29.83,0,0)
		self.box.setScale(1)
		
		self.box1 = loader.loadModel("models/box")
		self.box1.reparentTo(render)
		self.box1.setPos(-51.14,-17.90,0)
		self.box1.setScale(1)
		
		ralphStartPos = Vec3(-98.64,-20.60,0)
		self.ralph = Actor("models/ralph", {"run":"models/ralph-run", "walk":"models/ralph-walk"})
		self.ralph.reparentTo(render)
		self.ralph.setScale(1)
		self.ralph.setPos(ralphStartPos)
		
		ralphaiStartPos = Vec3(-50,20,0)
		self.ralphai = Actor("models/ralph", {"run":"models/ralph-run", "walk":"models/ralph-walk"})
		
		self.pointer = loader.loadModel("models/arrow")
		self.pointer.setColor(1,0,0)
		self.pointer.setPos(-7.5,-1.2,0)
		self.pointer.setScale(3)
		self.pointer.reparentTo(render)
		
		self.pointer1 = loader.loadModel("models/arrow")
		self.pointer1.setColor(1,0,0)
		self.pointer1.setPos(-98.64,-20.60,0)
		self.pointer1.setScale(3)
		
		self.floater = NodePath(PandaNode("floater"))
		self.floater.reparentTo(render)
		
		self.accept("escape", sys.exit)
		self.accept("enter", self.activateCam)
		self.accept("arrow_left", self.setKey, ["left",1])
		self.accept("arrow_right", self.setKey, ["right",1])
		self.accept("arrow_up", self.setKey, ["forward",1])
		self.accept("a", self.setKey, ["cam-left",1])
		self.accept("s", self.setKey, ["cam-right",1])
		self.accept("arrow_left-up", self.setKey, ["left",0])
		self.accept("arrow_right-up", self.setKey, ["right",0])
		self.accept("arrow_up-up", self.setKey, ["forward",0])
		self.accept("a-up", self.setKey, ["cam-left",0])
		self.accept("s-up", self.setKey, ["cam-right",0])
		
		self.isMoving = False
		
		self.cTrav = CollisionTraverser()
		
		self.ralphGroundRay = CollisionRay()
		self.ralphGroundRay.setOrigin(0,0,1000)
		self.ralphGroundRay.setDirection(0,0,-1)
		self.ralphGroundCol = CollisionNode('ralphRay')
		self.ralphGroundCol.addSolid(self.ralphGroundRay)
		self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
		self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
		self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
		self.ralphGroundHandler = CollisionHandlerQueue()
		self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)
		
		self.camGroundRay = CollisionRay()
		self.camGroundRay.setOrigin(0,0,1000)
		self.camGroundRay.setDirection(0,0,-1)
		self.camGroundCol = CollisionNode('camRay')
		self.camGroundCol.addSolid(self.camGroundRay)
		self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
		self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
		self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
		self.camGroundHandler = CollisionHandlerQueue()
		self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
		
		self.setAI()
		
	def activateCam(self):
		self.switchCam = not self.switchCam
		if (self.switchCam == True):
			base.cam.setPosHpr(0,0,0,0,0,0)
			base.cam.reparentTo(self.ralph)
			base.cam.setY(base.cam.getY() + 30)
			base.cam.setZ(base.cam.getZ() + 10)
			base.cam.setHpr(180,-15,0)
		else:
			base.cam.reparentTo(render)
			base.cam.setPosHpr(17.79, -87.64, 90.16, 38.66, 325.36, 0)
			
	def setKey(self, key, value):
		self.keyMap[key] = value
		
	def move(self):
		elapsed = globalClock.getDt()
		
		if (self.switchState == False):
			base.camera.lookAt(self.ralph)
			if (self.keyMap["cam-left"] != 0):
				base.camera.setX(base.camera, -(elapsed*20))
			if (self.keyMap["cam-right"] != 0):
				base.camera.setX(base.camera, +(elapsed*20))
				
		startpos = self.ralph.getPos()
		
		if (self.keyMap["left"]!=0):
			self.ralph.setH(self.ralph.getH() + elapsed*300)
		if (self.keyMap["right"]!=0):
			self.ralph.setH(self.ralph.getH() - elapsed*300)
		if (self.keyMap["forward"]!=0):
			self.ralph.setY(self.ralph, -(elapsed*25))
			
		if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
			if self.isMoving is False:
				self.ralph.loop("run")
				self.isMoving = True
		else:
			if self.isMoving:
				self.ralph.stop()
				self.ralph.pose("walk",5)
				self.isMoving = False
			
		if (self.switchState==False):
			camvec = self.ralph.getPos() - base.camera.getPos()
			camvec.setZ(0)
			camdist = camvec.length()
			camvec.normalize()
			if (camdist > 10.0):
				base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
				camdist = 10.0
			if (camdist < 5.0):
				base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
				camdist = 5.0
				
		self.cTrav.traverse(render)
		
		
		entries = []
		for i in range(self.ralphGroundHandler.getNumEntries()):
			entry = self.ralphGroundHandler.getEntry(i)
			entries.append(entry)
		entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		
		if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
			self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
		else:
			self.ralph.setPos(startpos)
			
		if (self.switchState==False):
			entries = []
			for i in range(self.camGroundHandler.getNumEntries()):
				entry = self.camGroundHandler.getEntry(i)
				entries.append(entry)
			entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		
			if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
				base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
			if (base.camera.getZ() < self.ralph.getZ() + 2.0):
				base.camera.setZ(self.ralph.getZ() + 2.0)
				
			self.floater.setPos(self.ralph.getPos())
			self.floater.setZ(self.ralph.getZ() + 2.0)
			base.camera.setZ(base.camera.getZ())
			base.camera.lookAt(self.floater)
			
		self.ralph.setP(0)
		return Task.cont
		
	def setAI(self):
		self.AIworld = AIWorld(render)
		
		self.accept("space", self.setMove)
		self.AIchar = AICharacter("ralph", self.ralph, 60, 0.05, 25)
		self.AIworld.addAiChar(self.AIchar)
		self.AIbehaviors = self.AIchar.getAiBehaviors()
		
		self.AIbehaviors.initPathFind("models/navmesh.csv")
		
		taskMgr.add(self.AIUpdate, "AIUpdate")
		
	def setMove(self):
		self.AIbehaviors.addStaticObstacle(self.box)
		self.AIbehaviors.addStaticObstacle(self.box1)
		self.AIbehaviors.pathFindTo(self.pointer)
		self.ralph.loop("run")
		
	def AIUpdate(self, task):
		self.AIworld.update()
		self.move()
		
		if (self.path_no == 1 and self.AIbehaviors.behaviorStatus("pathfollow") == "done"):
			self.path_no = 2
			self.AIbehaviors.pathFindTo(self.pointer1, "addPath")
			print("inside")
			
		if (self.path_no == 2 and self.AIbehaviors.behaviorStatus("pathfollow") == "done"):
			print("inside2")
			self.path_no = 1
			self.AIbehaviors.pathFindTo(self.pointer, "addPath")
			
		return Task.cont
		
w = World()
run()