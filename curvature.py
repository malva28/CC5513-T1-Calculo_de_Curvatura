from normals import calculate_vertex_normals_by_angle
import openmesh
import numpy as np
import polyscope as ps
from normals import calculate_vertex_normals_by_angle, calculate_vertex_face_angles, angle_sine


def calculate_curvature_o_edge_in_vertex_face(mesh: openmesh.TriMesh) -> np.ndarray:
    norm_by_angle = calculate_vertex_normals_by_angle(mesh)

    empty_dicts = np.frompyfunc(lambda x: {}, 1, 1)
    vertex_edge_curvatures = empty_dicts(np.zeros(mesh.n_vertices(), dtype=dict))
    for face in mesh.faces():
        p_vertices = [v.idx() for v in mesh.fv(face)]
        vertices = [mesh.points()[v_i] for v_i in p_vertices]
        for i in range(3):
            i_next = (i + 1) % 3
            vert_diff = vertices[i_next] - vertices[i]
            norm_diff = norm_by_angle[p_vertices[i_next]] - norm_by_angle[p_vertices[i]]

            curv = np.dot(norm_diff, vert_diff)/np.dot(vert_diff, vert_diff)

            vertex_edge_curvatures[p_vertices[i]][face.idx()] = curv

    return vertex_edge_curvatures


def calculate_vertex_mean_curvature(mesh: openmesh.TriMesh) -> np.ndarray:
    curvature_outgoing_edge = calculate_curvature_o_edge_in_vertex_face(mesh)

    vertex_curvatures = np.zeros(mesh.n_vertices())
    for vertex in mesh.vertices():
        i_v = vertex.idx()
        n_faces = 0
        for face in mesh.vf(vertex):
            vertex_curvatures[i_v] += curvature_outgoing_edge[i_v][face.idx()]
            n_faces += 1
        vertex_curvatures[i_v] = vertex_curvatures[i_v]/n_faces

    return vertex_curvatures


def calculate_vertex_angle_curvature(mesh: openmesh.TriMesh) -> np.ndarray:
    curvature_outgoing_edge = calculate_curvature_o_edge_in_vertex_face(mesh)
    vertex_face_angles = calculate_vertex_face_angles(mesh, method="sin")

    vertex_curvatures = np.zeros(mesh.n_vertices())
    for vertex in mesh.vertices():
        i_v = vertex.idx()
        face_list = [f for f in mesh.vf(vertex)]
        n_faces = len(face_list)
        angle_sum = 0
        for i in range(len(face_list)):
            face = face_list[i]
            prev_face = face_list[(i - 1) % n_faces]
            vertex_face_angle = vertex_face_angles[i_v][face.idx()]
            curv_sum = curvature_outgoing_edge[i_v][face.idx()] + curvature_outgoing_edge[i_v][prev_face.idx()]

            vertex_curvatures[i_v] += vertex_face_angle * curv_sum
            angle_sum += vertex_face_angle
        vertex_curvatures[i_v] = vertex_curvatures[i_v] / (2*angle_sum)

    return vertex_curvatures


if __name__ == "__main__":
    pth = "data/cat10.off"
    mesh = openmesh.read_trimesh(pth)
    arr = calculate_curvature_o_edge_in_vertex_face(mesh)

    face_curvature = np.zeros(mesh.n_faces())
    for i in range(mesh.n_vertices()):
        face_dict = arr[i]
        face_keys = [key for key in face_dict]
        for f_i in face_keys:
            face_curvature[f_i] += face_dict[f_i]
    face_curvature /= 3

    #arr2 = calculate_vertex_mean_curvature(mesh)
    arr2 = calculate_vertex_angle_curvature(mesh)

    ps.init()
    ps_mesh = ps.register_surface_mesh("my mesh", mesh.points(), mesh.face_vertex_indices())
    ps.get_surface_mesh("my mesh").add_scalar_quantity("vertex_face_curvatures",
                                                       face_curvature,
                                                       defined_on="faces",
                                                       enabled=True,
                                                       cmap="viridis")
    ps.get_surface_mesh("my mesh").add_scalar_quantity("vertex_mean_curvatures",
                                                       arr2,
                                                       defined_on="vertices",
                                                       enabled=True,
                                                       cmap="viridis",
                                                       vminmax=np.percentile(arr2, [10, 90]))
    ps.show()