import glm

class PointLight ():
    """
    A light source for shading
    """

    def __init__ (self, pos, color):
        """
        Constructor
        Receives the position and color of the point light source
        """
        self.position = pos
        self.color = color



