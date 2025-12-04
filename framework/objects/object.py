from pyglm import glm

class Object:
    def __init__(self, transform=glm.mat4(1)):
        """
        Base scene object: only holds a transform.
        """
        self.transform = transform

    def set_transform(self, transform):
        self.transform = transform

    def get_transform(self):
        return self.transform
