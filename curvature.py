import openmesh
import numpy as np
from normals import calculate_vertex_normals_by_angle, calculate_vertex_face_angles


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
        n_faces = np.max((1e-8, n_faces))
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
        angle_sum = np.max((angle_sum, 1e-8))
        vertex_curvatures[i_v] = vertex_curvatures[i_v] / (2*angle_sum)

    return vertex_curvatures
