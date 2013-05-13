import direct.directbase.DirectStart
from stratcam import CameraHandler
from pandac.PandaModules import *

from direct.task import Task
from direct.actor import Actor
import math

environ = loader.loadModel("models/environment")
environ.reparentTo(render)
environ.setScale(0.25, 0.25, 0.25)
environ.setPos(-8, 42, 0)

camHandler = CameraHandler()

pandaActor = Actor.Actor("models/panda-model", {"walk":"models/panda-walk4"})
pandaActor.setScale(0.005, 0.005, 0.005)
pandaActor.reparentTo(render)
pandaActor.loop("walk")
run()