# shader manager for GLSL

import OpenGL.GL as gl

def readShaderFile (filename):
    """
    Reads one shader file into a string
    """
    data = open(filename, 'r').read()
    return data

def createShader(vtx_filename, frag_filename, defines=None):
    vtx_source = readShaderFile(vtx_filename)
    frag_source = readShaderFile(frag_filename)

    if defines:
        define_str = "\n".join(f"#define {d}" for d in defines) + "\n"
        # Insert defines after the first line if it starts with #version
        def inject_defines(src):
            lines = src.splitlines(True)
            if lines and lines[0].startswith("#version"):
                return lines[0] + define_str + "".join(lines[1:])
            else:
                return define_str + src
        vtx_source = inject_defines(vtx_source)
        frag_source = inject_defines(frag_source)

    return createShaderFromString(vtx_source, frag_source)


def createShaderFromString(vtx_source, frag_source):
    """
    Creates a shader program from two input strings with GLSL code
    """
    
    # build and compile our shader program
    # vertex shader
    vertexShader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertexShader, vtx_source)  # INFO: Changed method head in PyOpenGL
    gl.glCompileShader(vertexShader)

    # check for shader compile errors
    success = gl.glGetShaderiv(vertexShader, gl.GL_COMPILE_STATUS)
    if not success:
        info_log = gl.glGetShaderInfoLog(vertexShader)
        raise Exception("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n%s" % info_log)
    
    # fragment shader
    fragmentShader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragmentShader, frag_source)  # Changed!
    gl.glCompileShader(fragmentShader)

    # check for shader compile errors
    success = gl.glGetShaderiv(fragmentShader, gl.GL_COMPILE_STATUS)
    if not success:
        info_log = gl.glGetShaderInfoLog(fragmentShader)
        raise Exception("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n%s" % info_log)

    # link shaders
    shaderProgram = gl.glCreateProgram()
    gl.glAttachShader(shaderProgram, vertexShader)
    gl.glAttachShader(shaderProgram, fragmentShader)
    gl.glLinkProgram(shaderProgram)

    # check for linking errors
    success = gl.glGetProgramiv(shaderProgram, gl.GL_LINK_STATUS)
    if not success:
        info_log = gl.glGetProgramInfoLog(shaderProgram, 512, None)
        raise Exception("ERROR::SHADER::PROGRAM::LINKING_FAILED\n%s" % info_log)

    gl.glDeleteShader(vertexShader)
    gl.glDeleteShader(fragmentShader)

    return shaderProgram

