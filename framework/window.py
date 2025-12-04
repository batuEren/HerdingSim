import glfw
from pyglm import glm
import OpenGL.GL as gl


class OpenGLWindow ():

    def __init__(self,  width: 400, height: 400, title: str = 'opengl'):
        super().__init__()

        self.title = title
        self.width = width
        self.height = height
        self.camera = None

        self.left_button_pressed = False
        self.right_button_pressed = False


        self.init_glfw ()
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)

        if self.window is None:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")
        
        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        glfw.set_window_size_callback(self.window, self.window_size_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)

    def delete (self):
        glfw.terminate()

    def init_glfw (self):
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    def window_size_callback(self, window, width, height):
        gl.glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.camera.window_size_callback(width, height)
        # self.projection = glm.perspective(self.radians, width / height, self.near, self.far)

    # when window size changed (by OS or user resize) this callback function executes
    def framebuffer_size_callback(self, window, width, height):
        print("Window resized.")
        # make sure the viewport matches the new window dimensions; note that width and 
        #gl.glViewport(0, 0, width, height)

    def scroll_callback(self, window, x_offset, y_offset):
        self.camera.scroll (y_offset)
    
    # mouse callback, mainly for controlling camera and UI
    def mouse_button_callback(self, window, button, action, mods):
            
            x, y = glfw.get_cursor_pos(self.window)

            #self.set_current_cursor(self.cursor_pos, self.cursor_dir)
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                self.camera.set_init_transform(x, y)
                self.left_button_pressed = True

            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
                 self.left_button_pressed = False

            if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
                 self.right_button_pressed = True

            if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
                 self.right_button_pressed = False

    # mouse move callback
    def cursor_pos_callback(self, window, x_pos, y_pos):
            x, y = glfw.get_cursor_pos(self.window)
            if self.left_button_pressed:
                self.camera.set_cur_transform(x, y)



    # keyboard callback
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if action == glfw.PRESS:
            self.camera.key_press(key)
        
        if action == glfw.REPEAT:
             self.camera.key_repeat(key)
        
        if action == glfw.RELEASE:
             self.camera.key_release(key)


        #if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS: