from pyglm import glm
import glfw

from framework.materials.shaders import *
# from mesh import *

class Camera ():
    """
    Camera is an abstract class
    """    

    def __init__(self, width, height, fov, near, far):

        self.width = width
        self.height = height
        self.aspect_ratio = self.width/self.height
        self.fov = fov
        self.near = near
        self.far = far
        self.view = glm.mat4(1)
 
        self.compute_projection_matrix()

    def compute_projection_matrix(self):
        self.projection = glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)

    def rotate(self, angle, axis):
        self.view = glm.rotate(self.view, angle, axis)

    def draw(self):
        pass
    
    def scroll(self, offset):
        pass
    
    def set_init_transform(self, x, y):
        pass

    def set_cur_transform(self, x, y):
        pass

    def key_press (self, key):
        pass

    def key_release (self, key):
        pass

    def key_repeat (self, key):
        pass

    def window_size_callback(self, width, height):
        self.width = width
        self.height = height
        self.aspect_ratio = self.width/self.height
        self.compute_projection_matrix()

# Default fragment shader for rendering trackball representation.
trackball_fragment_code = """
    #version 430 core
    in vec4 ex_Color;
    out vec4 out_Color;
    in float depth;
    void main(void)
    {
        out_Color = ex_Color;
        gl_FragDepth = depth;
    }"""

# Default vertex shader for rendering trackball representation.
trackball_vertex_code = """
    #version 430 core
    layout(location=0) in vec4 in_position;

    out vec4 ex_Color;
    out float depth;
    
    uniform vec4 in_color;
    
    uniform mat4 modelMatrix;
    uniform mat4 viewMatrix;
    uniform mat4 projectionMatrix;

    uniform float nearPlane;
    uniform float farPlane;
    
    void main(void)
    {
        vec4 pos = (viewMatrix * modelMatrix) * in_position;
        depth = (farPlane+nearPlane)/(farPlane-nearPlane) + ( (2*nearPlane*farPlane)/(farPlane-nearPlane) ) * (1/pos[2]);
        depth = (depth+1.0)/2.0;
        gl_Position = projectionMatrix * pos;
        ex_Color = in_color;
    }"""

class Trackball (Camera):
    """
    Trackball implementation
    """
    def __init__ (self, width, height, fov, near, far):

        super().__init__(width, height, fov, near, far)

        # initial screen space position (mouse click)
        self.init_pos = glm.vec2(0)
        # initial direction of trackball direction
        self.init_dir = glm.vec3(0)
        # current screen space position of mouse
        self.cur_pos = glm.vec2(0)
        # current direction of trackball direction
        self.cur_dir = glm.vec3(0)

        self.radius = 0.8
        self.zoom_factor = 1

        # translation of the representation (not zoom factor)
        self.default_translation = glm.translate(glm.vec3(0, 0, -4)) 
        self.rotation = glm.mat4(1)
        self.model = glm.mat4(1)
        
        # transform is the matrix used to scale and translate the camera (not the representation) 
        self.transform = glm.translate(glm.vec3(0, 0, -self.zoom_factor))
        
        # camera view applied to scene
        self.view = glm.mat4(1)
        
        self.updateView()
        

        # below is the mesh and shaders to render the trackball representation
        # self.mesh = Mesh()
        self.createTrackballRepresentation()

        self.shader_program = createShaderFromString(trackball_vertex_code, trackball_fragment_code)
        

    def createTrackballRepresentation (self):
        """
        A circle. It is drawn three times with rotations to represent the 3 DoF
        """
        # segs = 32
        # pos = glm.vec4(self.radius, 0, 0, 1)
        # # create segs points on a circle
        # for i in range (0, segs+1):
        #     p = glm.rotate(glm.radians(i*360/segs), glm.vec3(0, 1, 0)) * pos
        #     self.mesh.vertices = np.append(self.mesh.vertices, p)
        # self.mesh.createBuffers()

    def rotate(self, angle, axis):
        """
        Rotate the view matrix given an angle and axis
        """
        self.rotation = glm.rotate(angle, axis) * self.rotation
        self.updateView()

    def scroll(self, offset):
        self.zoom_factor += offset*0.1
        self.transform = glm.translate(glm.vec3(0, 0, -self.zoom_factor))
        self.updateView()
        
    def updateView (self):
        self.view = self.transform * self.default_translation * self.rotation

    # sets the pos and trackball direction for current mouse position
    def project_pos_to_sphere (self, pos):
        
        # convert from pixel coords to normalized coords [-1,1]
        dir = glm.vec3(2*(pos.x / (self.width - 1)) - 1, 1 - 2*(pos.y / (self.height - 1)), 0)

        d = dir.x*dir.x + dir.y*dir.y
        # cursor inside sphere, use spherical function
        if d <= self.radius*self.radius*0.5:
            dir.z = glm.sqrt(1 - d)
        # cursor outside, use hyperbolic function
        else:
            dir.z = (self.radius*self.radius)/(2*glm.sqrt(d))

        return glm.normalize(dir)

    # set the initial click position and trackball direction
    def set_init_transform (self, x, y):
        self.init_pos = glm.vec2(x, y)
        self.init_dir = self.project_pos_to_sphere (self.init_pos)

    # set the initial click position and trackball direction and compute the trackball transformation
    def set_cur_transform (self, x, y):
        self.cur_pos = glm.vec2(x, y)
        self.cur_dir = self.project_pos_to_sphere (self.cur_pos)

        if self.cur_dir == self.init_dir:
            return
        
        # angle between initial and current direction
        # directions should be normalized at this point
        angle = glm.acos( glm.dot(self.init_dir, self.cur_dir) )

        # rotation axis
        dir = glm.normalize (glm.cross (self.init_dir, self.cur_dir))

        self.rotate(angle, dir)

        # update initial transform to work with small increments
        self.init_pos = self.cur_pos
        self.init_dir = self.cur_dir

    def draw (self):
        gl.glUseProgram(self.shader_program)
        gl.glBindVertexArray(self.mesh.VAO)

        loc_model = gl.glGetUniformLocation(self.shader_program, "modelMatrix")
        loc_view = gl.glGetUniformLocation(self.shader_program, "viewMatrix")
        loc_projection = gl.glGetUniformLocation(self.shader_program, "projectionMatrix")
        loc_near = gl.glGetUniformLocation(self.shader_program, "nearPlane")
        loc_far = gl.glGetUniformLocation(self.shader_program, "farPlane")
        loc_color = gl.glGetUniformLocation(self.shader_program, "in_color")
        
        # here we pass only the rotation since we do not want to scale or translate the representation
        rep_view = self.default_translation * self.rotation
        gl.glUniformMatrix4fv(loc_view, 1, gl.GL_FALSE, glm.value_ptr(rep_view))
        gl.glUniformMatrix4fv(loc_projection, 1, gl.GL_FALSE, glm.value_ptr(self.projection))
        gl.glUniform1f(loc_near, self.near)
        gl.glUniform1f(loc_far, self.far)

        # draw y-axis
        self.model = glm.mat4(1)
        color = glm.vec4(0.0, 1.0, 0.0, 0.0)
        gl.glUniform4fv (loc_color, 1, glm.value_ptr(color))
        gl.glUniformMatrix4fv(loc_model, 1, gl.GL_FALSE, glm.value_ptr(self.model))        
        gl.glDrawArrays(gl.GL_LINE_LOOP, 0, len(self.mesh.vertices))
        
        # draw z-axis
        self.model = glm.rotate(self.model, glm.half_pi(), glm.vec3(1.0, 0.0, 0.0) )
        color = glm.vec4(0.0, 0.0, 1.0, 0.0)
        gl.glUniformMatrix4fv(loc_model, 1, gl.GL_FALSE, glm.value_ptr(self.model))
        gl.glUniform4fv (loc_color, 1, glm.value_ptr(color))
        gl.glDrawArrays(gl.GL_LINE_LOOP, 0, len(self.mesh.vertices))
        
        # draw x-axis
        self.model = glm.rotate(self.model, glm.half_pi(), glm.vec3(0.0, 0.0, 1.0) )
        color = glm.vec4(1.0, 0.0, 0.0, 0.0)
        gl.glUniformMatrix4fv(loc_model, 1, gl.GL_FALSE, glm.value_ptr(self.model))
        gl.glUniform4fv (loc_color, 1, glm.value_ptr(color))
        gl.glDrawArrays(gl.GL_LINE_LOOP, 0, len(self.mesh.vertices))

        gl.glBindVertexArray(0)


class Flycamera (Camera):
    """
    Flycamera implementation
    Move the camera using ASWD and mouse
    """
    def __init__ (self, width, height, fov, near, far):

        super().__init__(width, height, fov, near, far)

        # size of step when using ASWD
        self.step_factor = 0.6
        # rotation sensitivity
        self.rot_sensitivity = 0.1

        # last screen space position (mouse click)
        self.last_pos = glm.vec2(0)
        # current screen space position of mouse
        self.cur_pos = glm.vec2(0)

        self.current_frame = 0.0
        self.last_frame = 0.0

        # transformation of the camera
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)

        self.position = glm.vec3(0, 0, 3)

        # pitch, yaw, row
        self.euler_angles = glm.vec3(0, -90.0, 0)  

        self.model = glm.mat4(1)
        
        # camera view applied to scene
        self.view = glm.mat4(1)

        self.updateView()
 
 

    def rotate(self, angle, axis):
        """
        Rotate the view matrix given an angle and axis
        """
        self.rotation = glm.rotate(angle, axis) * self.rotation

    def updateView (self):
        self.right = glm.normalize(glm.cross(self.front, self.up))
        self.view = glm.lookAt (self.position, self.position + self.front, self.up)

    # set the initial click position and trackball direction
    def set_init_transform (self, x, y):
        self.last_pos = glm.vec2(x, y)
    
    # set the initial click position and trackball direction and compute the trackball transformation
    def set_cur_transform (self, x, y):
        self.cur_pos = glm.vec2(x, y);
        delta_x = self.cur_pos.x - self.last_pos.x
        delta_y = self.last_pos.y - self.cur_pos.y
        self.last_pos = self.cur_pos

        self.euler_angles.x += delta_y * self.rot_sensitivity
        self.euler_angles.y += delta_x * self.rot_sensitivity

        self.front = glm.normalize( glm.vec3(glm.cos(glm.radians(self.euler_angles.y)) * glm.cos(glm.radians(self.euler_angles.x)),
                            glm.sin(glm.radians(self.euler_angles.x)),
                            glm.sin(glm.radians(self.euler_angles.y)) * glm.cos(glm.radians(self.euler_angles.x)) ))

        self.updateView()



    def key_press (self, key):

        if key == glfw.KEY_W:
             self.position += self.front * self.step_factor
        elif key == glfw.KEY_S:
             self.position -= self.front * self.step_factor
        elif key == glfw.KEY_A:
             self.position -= self.right * self.step_factor
        elif key == glfw.KEY_D:
             self.position += self.right * self.step_factor
        elif key == glfw.KEY_E:
             self.position += self.up * self.step_factor
        elif key == glfw.KEY_C:
             self.position -= self.up * self.step_factor
        
        self.updateView()

    def key_repeat(self, key):
        self.key_press (key)
