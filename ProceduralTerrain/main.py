from basicfunctions import * 
from camera import *
from config import *
from creature import *
import direct.directbase.DirectStart
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from gui import *
from pandac.PandaModules import LightRampAttrib
from pandac.PandaModules import PStatClient
from sky import *
from splashCard import *
from terrain import *
from waterNode import *
from mapeditor import *
from physics import *

#if __name__ == "__main__":
logging.info("Hello World")

class World(DirectObject):
	def __init__(self):
		# set here your favorite background color - this will be used to fade to
		bgcolor = (0.2, 0.2, 0.2, 1)
		base.setBackgroundColor(*bgcolor)
		self.splash = SplashCard('textures/loading.png', bgcolor)
		taskMgr.doMethodLater(0.01, self.load, "Load Task")
		self.bug_text = addText(-0.95, "Loading...", True, scale=0.1)
		
	def load(self, task):
		PStatClient.connect()
		
		self.bug_text.setText("loading Display...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadDisplay()
		
		self.bug_text.setText("loading physics...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadPhysics()
		
		self.bug_text.setText("loading sky...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadSky()
		
		#Definitely need to make sure this loads before terrain
		self.bug_text.setText("loading terrain...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadTerrain()
		yield Task.cont
		yield Task.cont
		while taskMgr.hasTaskNamed("preloadTask"):
			#loggin.info("waiting")
			yield Task.cont
		logging.info("terrain preloaded")
		
		#self.bug_text.setText("loading fog...")
		#showFrame()
		#self._loadFog()
		
		self.bug_text.setText("loading player...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadPlayer()
		
		self.bug_text.setText("loading water...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadWater()
		
		self.bug_text.setText("loading filters...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadFilters()
		
		self.bug_text.setText("loading gui controls...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self._loadGui()
		
		self.bug_text.setText("loading miscellanous...")
		#showFrame()
		yield Task.cont
		yield Task.cont
		
		self.physics.setup(self.terrain, self.ralph)
		
		taskMgr.add(self.move, "moveTask")
		
		# Game state variables
		self.prevtime = 0
		self.isMoving = False
		self.firstmove = 1
		
		disableMouse()
		
		self.bug_text.setText("")
		#showFrame()
		yield Task.cont
		yield Task.cont
		self.splash.destroy()
		self.splash = None
		
		yield Task.done
		
	def _loadGui(self):
		try:
			self.terrain.texturer.shader
		except:
			logging.info("Terrain texturer has no shader to control.")
		else:
			self.shaderControl = TerrainShaderControl(-0.4, -0.1, self.terrain)
			self.shaderControl.hide()
			
	def _loadDisplay(self):
		base.setFrameRateMeter(True)
		#base.win.setClearColor(Vec4(0,0,0,1))
		# Post the instructions
		self.title = addTitle("Animate Dream Terrain Engine")
		self.inst1 = addText(0.95, "[ESC]: Quit")
		self.inst2 = addText(0.90, "[Mouse Wheel]: Camera Zoom")
		self.inst3 = addText(0.85, "[Y]: Y-axis Mouse Invert")
		self.inst4 = addText(0.80, "[W]: Run Character Forward")
		self.inst5 = addText(0.75, "[A]: Run Character Left")
		self.inst6 = addText(0.70, "[S]: Run Character Backward")
		self.inst7 = addText(0.65, "[D]: Run Character Right")
		self.inst8 = addText(0.60, "[Shift]: Turbo Mode")
		self.inst9 = addText(0.55, "[R]: Regenerate Terrain")
		self.inst10 = addText(0.50, "[Tab]: Open Shader Controls")
		self.inst11 = addText(0.45, "[1-8]: Set time to # * 3")
		self.inst12 = addText(0.40, "[N]: Toggle Night Skipping")
		self.inst13 = addText(0.35, "[P]: Pause day night cycle")
		self.inst14 = addText(0.30, "[F11]: Screen Shot")
		self.inst15 = addText(0.25, "[T]: Special Test")
		
		self.loc_text = addText(0.15, "[POS]: ", True)
		self.hpr_text = addText(0.10, "[HPR]: ", True)
		self.time_text = addText(0.05, "[Time]: ", True)
		
	def _loadTerrain(self):
		populator = TerrainPopulator()
		populator.addObject(makeTree, {}, 5)
		
		if SAVED_HEIGHT_MAPS:
			seed = 666
		else:
			seed = 0
		self.terrain = Terrain('Terrain', base.cam, MAX_VIEW_RANGE, populator, feedBackString = self.bug_text, id=seed)
		self.terrain.reparentTo(render)
		self.editor = MapEditor(self.terrain)
		
	def _loadWater(self):
		self._water_level = self.terrain.maxHeight * self.terrain.waterHeight
		size = self.terrain.maxViewRange * 1.5
		self.water = WaterNode(self, -size, -size, size, size, self._water_level)
		
	def _loadFilters(self):
		self.terrain.setShaderInput('waterlevel', self._water_level)
		
		# load default shaders
		cf = CommonFilters(base.win, base.cam)
		# bloomSize
		cf.setBloom(size='small', desat=0.7, intensity=1.5, mintrigger=0.6, maxtrigger=0.95)