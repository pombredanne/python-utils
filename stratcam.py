from direct.showbase import DirectObject
from pandac.PandaModules import Vec3, Vec2
import math

class CameraHandler(DirectObject.DirectObject):
	def __init__(self):
	
		base.disableMouse()
		base.camera.setPos(0,20,20)
		base.camera.lookAt(0,0,0)
		
		self.mx, self.my = 0,0
		self.orbiting = False
		
		self.target = Vec3()
		
		self.camDist = 40
		
		self.panRateDivisor = 20
		
		self.panZoneSize = .15
		
		self.panLimitsX = Vec2(-20, 20)
		self.panLimitsY = Vec2(-20, 20)
		
		self.setTarget(0,0,0)
		self.turnCameraAroundPoint(0,0)
		
		self.accept("mouse3", self.startOrbit)		
		self.accept("mouse3-up", self.stopOrbit)
		self.accept("wheel_up", lambda : self.adjustCamDist(0.9))
		self.accept("wheel_down", lambda : self.adjustCamDist(1.1))
		
		taskMgr.add(self.camMoveTask, 'camMoveTask')
		
	def turnCameraAroundPoint(self, deltaX, deltaY):
		
		newCamHpr = Vec3()
		newCamPos = Vec3()
		
		camHpr = base.camera.getHpr()
		
		newCamHpr.setX(camHpr.getX()+deltaX)
		newCamHpr.setY(self.clamp(camHpr.getY()-deltaY, -85, -10))
		newCamHpr.setZ(camHpr.getZ())
		
		base.camera.setHpr(newCamHpr)
		
		angleradiansX = newCamHpr.getX() * (math.pi / 180.0)
		angleradiansY = newCamHpr.getY() * (math.pi / 180.0)
		
		newCamPos.setX(self.camDist*math.sin(angleradiansX)*math.cos(angleradiansY)+self.target.getX())
		newCamPos.setY(-self.camDist*math.cos(angleradiansX)*math.cos(angleradiansY)+self.target.getY())
		newCamPos.setZ(-self.camDist*math.sin(angleradiansY)+self.target.getZ())
		base.camera.setPos(newCamPos.getX(), newCamPos.getY(), newCamPos.getZ())
		
		base.camera.lookAt(self.target.getX(), self.target.getY(), self.target.getZ())
		
	def setTarget(self,x,y,z):
		x = self.clamp(x, self.panLimitsX.getX(), self.panLimitsX.getY())
		self.target.setX(x)
		y = self.clamp(y, self.panLimitsY.getX(), self.panLimitsY.getY())
		self.target.setY(y)
		self.target.setZ(z)
		
	def setPanLimits(self,xMin, xMax, yMin, yMax):
		self.panLimitsX = (xMin, xMax)
		self.panLimitsY = (yMin, yMax)
		
	def clamp(self, val, minVal, maxVal):
		val = min(max(val, minVal), maxVal)
		return val
		
	def startOrbit(self):
		self.orbiting = True
		
	def stopOrbit(self):
		self.orbiting = False
		
	def adjustCamDist(self, distFactor):
		self.camDist = self.camDist*distFactor
		self.turnCameraAroundPoint(0,0)
		
	def camMoveTask(self, task):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			
			if self.orbiting:
				self.turnCameraAroundPoint((self.mx-mpos.getX())*100, (self.my-mpos.getY())*100)
			else:
				moveY = False
				moveX = False
				
				if self.my > (1 - self.panZoneSize):
					angleradiansX1  = base.camera.getH() * (math.pi / 180.0)
					panRate1 = (1 - self.my - self.panZoneSize) * (self.camDist / self.panRateDivisor)
					moveY = True
				if self.my < (-1 + self.panZoneSize):
					angleradiansX1 = base.camera.getH() * (math.pi / 180.0) + math.pi
					panRate1 = (1 + self.my - self.panZoneSize)*(self.camDist / self.panRateDivisor) 
					moveY = True
				if self.mx > (1 - self.panZoneSize):
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0) + math.pi * 0.5
					panRate2 = (1 - self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor)
					moveX = True
				if self.mx < (-1 + self.panZoneSize):
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0) - math.pi * 0.5
					panRate2 = (1 + self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor)
					moveX = True
					
					
				if moveY:
					tempX = self.target.getX() + math.sin(angleradiansX1) * panRate1
					tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
					self.target.setX(tempX)
					tempY = self.target.getY() - math.cos(angleradiansX1) * panRate1
					tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
					self.target.setY(tempY)
					self.target.setY(tempY)
					self.turnCameraAroundPoint(0,0)
				if moveX:
					tempX = self.target.getX() - math.sin(angleradiansX2) * panRate2
					tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
					self.target.setX(tempX)
					tempY = self.target.getY() + math.cos(angleradiansX2) * panRate2
					tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
					self.target.setY(tempY)
					self.turnCameraAroundPoint(0,0)
					
			print (self.target)
			self.mx = mpos.getX()
			self.my = mpos.getY()
			
		return task.cont