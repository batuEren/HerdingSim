import numpy as np
import glfw
import OpenGL.GL as gl

import sys

from .window import *
from .shapes import *
from .light  import *

class GLRenderer ():
    """
    Sets up a renderer with OpenGL
    The Renderer receives a Window and includes the necessary building blocks: camera and shapes array
    and a simple draw function
    """


    def __init__ (self, window, camera):
        """
        Constructor
        Receives a Window 
        The Renderer receives an OpenGLWindow and creates a default camera (Trackball)
        """
        self.glwindow = window
    
        # set the camera for the callbacks
        self.glwindow.camera = camera

        self.objects = []

        # light sources
        self.lights = []

    def setCamera (self, camera):
        self.glwindow.camera = camera

    def delete (self):
        return
    
    def addLight (self, light):
        self.lights.append(light)

    def addObject(self, obj):
        if not hasattr(obj, "draw") or not callable(getattr(obj, "draw")):
            print(f"[Renderer] Error: object {obj} has no callable draw() method", file=sys.stderr)
            return
        self.objects.append(obj)

    def render (self):
        gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        for o in self.objects:
            o.draw(self.glwindow.camera, self.lights)
            
        # if self.glwindow.camera.draw_camera:
            # print("fixme")
            # self.glwindow.camera.draw()
          
        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        glfw.swap_buffers(self.glwindow.window)
        glfw.poll_events()

