import openmesh
import polyscope as ps
from curvature import calculate_vertex_mean_curvature, calculate_vertex_angle_curvature
import numpy as np
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Cálculo de Curvaturas en Malla Triangular 3D',
        description='Calcula la curvatura de un cuerpo usando métodos discretos para mallas triangulares. '
                    'Grafica el resultado en Polyscope, usando mapeos de color en cada vértice.',
        epilog='Tarea 1 del curso CC5513: Procesamiento geométrico y análisis de formas')

    parser.add_argument('--file', default="data/esfera1.off", help="Ruta del archivo con la información de la malla "
                                                                   "triangular")  # positional argument
    parser.add_argument('--weight', default="const", choices=["const", "angles"],
                        help="Determina cómo ponderar las curvaturas para el cálculo por vértice.\n - const: se toma "
                             "promedio simple de las curvaturas de las aristas adyacentes\n - angle: se ponderan "
                             "curvaturas considerando el ángulo entre las aristas")
    parser.add_argument('--cmap', default="viridis", help="Mapa de colores para la curvatura mostrada en polyscope. "
                                                          "Opciones de colores disponibles en: "
                                                          "https://polyscope.run/py/features/color_maps/")
    parser.add_argument('--min-perc', dest="min_perc", default=10, type=float,
                        help="Trunca los valores mínimos de curvatura al "
                             "correspondiente al percentil ingresado. Valor "
                             "entre 0 y 100")
    parser.add_argument('--max-perc', dest="max_perc", default=90, type=float,
                        help="Trunca los valores máximos de curvatura al "
                             "correspondiente al percentil ingresado. Valor "
                             "entre 0 y 100")

    args = parser.parse_args()

    print("===== PROCESSING FILE: {}=====".format(args.file))
    print("args:\n\tweight = {}\n\tcmap = {}\n\tmin-perc = {}\n\tmax-perc = {}".format(
        args.weight,
        args.cmap,
        args.min_perc,
        args.max_perc))

    pth = args.file
    mesh = openmesh.read_trimesh(pth)

    if args.weight == "const":
        curvatures = calculate_vertex_mean_curvature(mesh)
    elif args.weight == "angles":
        curvatures = calculate_vertex_angle_curvature(mesh)

    print()
    print("n_vertices = {} ,\tn_faces = {}".format(mesh.n_vertices(), mesh.n_faces()))
    print("min_curvature = {} ,\tmax_curvature = {}".format(curvatures.min(), curvatures.max()))

    perc_limits = np.percentile(curvatures, [args.min_perc, args.max_perc])

    print("trunc_min_curvature = {} ,\ttrunc_max_curvature = {}".format(*perc_limits))

    ps.init()
    ps_mesh = ps.register_surface_mesh("my mesh", mesh.points(), mesh.face_vertex_indices())
    ps.get_surface_mesh("my mesh").add_scalar_quantity("vertex_mean_curvatures",
                                                       curvatures,
                                                       defined_on="vertices",
                                                       enabled=True,
                                                       cmap=args.cmap,
                                                       vminmax=perc_limits)
    ps.show()
