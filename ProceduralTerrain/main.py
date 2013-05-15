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