from window import *
from renderer import *
from shapes.shape import *
import os

def main():

    filedir = os.path.dirname(os.path.realpath(__file__))

    # GLFLW window
    glwindow = OpenGLWindow(600, 600)

    # opengl renderer
    glrenderer = GLRenderer(glwindow)
    glrenderer.setCamera (Trackball(glwindow.width, glwindow.height, 45.0, 0.1, 100.0))
    glrenderer.shapes.append( Shape(glm.vec3(1.0, 0.0, 0.0)) )

    # render loop
    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0

if __name__ == "__main__":
    main()
