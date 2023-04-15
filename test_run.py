import subprocess
import os
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Test de Cálculo de Curvaturas en Malla Triangular 3D',
        description='Corre automáticamente los modelos usados para el testeo del programa.',
        epilog='Tarea 1 del curso CC5513: Procesamiento geométrico y análisis de formas')

    parser.add_argument('--test-weight', dest="test_weight", default="all", choices=["all", "const", "angles"],
                        help="Corre las pruebas de curvatura usando la ponderación const (o promedio simple), "
                             "o por angles (ángulos). Si se elige all, se corren ambas pruebas")
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

    base = "data"
    python_exe = sys.executable

    tested_objs = [
        "cat1.off",
        "airplane_0627.off",
        "elephant-50kv.off"
    ]

    for filename in tested_objs:
        file_path = os.path.join(base, filename)
        weights = []
        if args.test_weight == "const" or args.test_weight == "all":
            weights.append("const")
        if args.test_weight == "angles" or args.test_weight == "all":
            weights.append("angles")
        for weight in weights:
            process = subprocess.run([python_exe, 'main.py',
                                      '--file', file_path,
                                      '--weight', weight,
                                      '--cmap', args.cmap,
                                      '--min-perc', str(args.min_perc),
                                      '--max-perc', str(args.max_perc)])
            ret = process.returncode
            print("== Subprocess finished with exit code {} ==".format(ret))
