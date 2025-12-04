# exporter_gltf.py
import numpy as np
from pathlib import Path
from pygltflib import (
    GLTF2, Asset, Scene, Node, Mesh, Primitive,
    Buffer, BufferView, Accessor
)

# glTF component type constants
COMPONENT_TYPE = {
    np.float32: 5126,   # FLOAT
    np.uint32: 5125,   # UNSIGNED_INT
    np.uint16: 5123,   # UNSIGNED_SHORT
    np.uint8:  5121,   # UNSIGNED_BYTE
}

def _align4(n): return (n + 3) & ~3

def _append_blob(gltf, data: np.ndarray, target=None):
    """Append numpy array to binary blob, return bufferView index."""
    if len(gltf.buffers) == 0:
        gltf.buffers.append(Buffer(byteLength=0))
    blob = gltf.binary_blob() or b""
    offset = len(blob)
    raw = data.tobytes()
    padded = raw + b"\x00" * (_align4(len(raw)) - len(raw))
    blob += padded
    gltf.set_binary_blob(blob)
    gltf.buffers[0].byteLength = len(blob)
    bv = BufferView(buffer=0, byteOffset=offset, byteLength=len(raw), target=target)
    gltf.bufferViews.append(bv)
    return len(gltf.bufferViews) - 1

def _make_accessor(gltf, bv_index, arr: np.ndarray, type_str: str):
    comp_type = COMPONENT_TYPE[arr.dtype.type]
    acc = Accessor(
        bufferView=bv_index,
        byteOffset=0,
        componentType=comp_type,
        count=arr.shape[0],
        type=type_str
    )
    if type_str == "VEC3":
        acc.min = arr.min(axis=0).tolist()
        acc.max = arr.max(axis=0).tolist()
    gltf.accessors.append(acc)
    return len(gltf.accessors) - 1

def _matrix_from(obj):
    M = getattr(obj, "transform", None)
    if M is None:
        return [1,0,0,0,
                0,1,0,0,
                0,0,1,0,
                0,0,0,1]
    try:
        matlist = M.to_list()
        return [item for row in matlist for item in row]
    except Exception:
        arr = np.array(M, dtype=np.float32).reshape(4,4)
        return arr.flatten().tolist()

def _pack_mesh(gltf, mesh_obj):
    m = mesh_obj.mesh
    if not hasattr(m, "vertices"):
        m.createGeometry()

    # positions
    positions = np.array(m.vertices, dtype=np.float32)
    if positions.shape[1] == 4:
        positions = positions[:, :3]
    pos_bv = _append_blob(gltf, positions, target=34962)
    pos_acc = _make_accessor(gltf, pos_bv, positions, "VEC3")

    # indices
    indices = np.array(m.indices, dtype=np.uint32)
    idx_bv = _append_blob(gltf, indices, target=34963)
    idx_acc = _make_accessor(gltf, idx_bv, indices, "SCALAR")

    attrs = {"POSITION": pos_acc}

    if hasattr(m, "normals") and m.normals is not None and len(m.normals):
        normals = np.array(m.normals, dtype=np.float32)
        nor_bv = _append_blob(gltf, normals, target=34962)
        nor_acc = _make_accessor(gltf, nor_bv, normals, "VEC3")
        attrs["NORMAL"] = nor_acc

    if hasattr(m, "uvs") and m.uvs is not None and len(m.uvs):
        uvs = np.array(m.uvs, dtype=np.float32)
        uv_bv = _append_blob(gltf, uvs, target=34962)
        uv_acc = _make_accessor(gltf, uv_bv, uvs, "VEC2")
        attrs["TEXCOORD_0"] = uv_acc

    if hasattr(m, "colors") and m.colors is not None and len(m.colors):
        colors = np.array(m.colors, dtype=np.float32)
        col_bv = _append_blob(gltf, colors, target=34962)
        col_acc = _make_accessor(gltf, col_bv, colors, "VEC4")
        attrs["COLOR_0"] = col_acc

    prim = Primitive(attributes=attrs, indices=idx_acc, mode=4)
    gltf.meshes.append(Mesh(primitives=[prim]))
    return len(gltf.meshes) - 1

def export_scene(renderer, filepath="scene.gltf"):
    gltf = GLTF2(asset=Asset(version="2.0"))
    gltf.scene = 0
    gltf.scenes = [Scene(nodes=[])]
    gltf.buffers = []
    gltf.bufferViews = []
    gltf.accessors = []
    gltf.meshes = []
    gltf.nodes = []
    gltf.set_binary_blob(b"")

    def add_node(mesh_index, matrix):
        node = Node(mesh=mesh_index, matrix=matrix)
        gltf.nodes.append(node)
        idx = len(gltf.nodes) - 1
        gltf.scenes[0].nodes.append(idx)
        return idx

    for obj in renderer.objects:
        if hasattr(obj, "mesh"):
            mesh_index = _pack_mesh(gltf, obj)
            if hasattr(obj, "transforms") and isinstance(obj.transforms, list):
                for T in obj.transforms:
                    class _Tmp: pass
                    tmp = _Tmp(); tmp.transform = T
                    add_node(mesh_index, _matrix_from(tmp))
            else:
                add_node(mesh_index, _matrix_from(obj))

    out = Path(filepath)
    gltf.save_json(out)
    if gltf.binary_blob():
        with open(out.with_suffix(".bin"), "wb") as f:
            f.write(gltf.binary_blob())

    print(f"[export] wrote {out} and {out.with_suffix('.bin')}")
