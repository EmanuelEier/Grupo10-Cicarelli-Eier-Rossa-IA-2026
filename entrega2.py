import itertools

from simpleai.search import CspProblem, backtrack, MOST_CONSTRAINED_VARIABLE, LEAST_CONSTRAINING_VALUE


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    variables = []

    for i in range(habs):
        variables.append(f"hab_{i}")

    for i in range(generators):
        variables.append(f"gen_{i}")

    for i in range(labs):
        variables.append(f"lab_{i}")

    for i in range(deposits):
        variables.append(f"dep_{i}")

    for i in range(airlocks):
        variables.append(f"air_{i}")

    dominios = {}

    def borde_mapa(fila, columna):
        return fila == camp_size[0]-1 or fila == 0 or columna == camp_size[1]-1 or columna == 0

    for variable in variables:
        dominios[variable] = []
        for fila in range(camp_size[0]):
            for columna in range(camp_size[1]):
                if (fila, columna) not in craters:
                    if variable.startswith("air"):
                        if borde_mapa(fila, columna):
                            dominios[variable].append((fila, columna))
                    elif variable.startswith("hab"):
                        if not borde_mapa(fila, columna):
                            dominios[variable].append((fila, columna))
                    else:
                        dominios[variable].append((fila, columna))

    restricciones = []

    def no_superposicion(variables, valores):
        return valores[0] != valores[1]

    for v1, v2 in itertools.combinations(variables, 2):
        restricciones.append(((v1, v2), no_superposicion))

    variables_gen = [v for v in variables if v.startswith("gen")]
    variables_hab = [v for v in variables if v.startswith("hab")]

    def no_adyacentes(variables, valores):
        (f1, c1) = valores[0]
        (f2, c2) = valores[1]

        return not (abs(f1 - f2) + abs(c1 - c2) == 1)

    for v1, v2 in itertools.product(tuple(variables_gen), tuple(variables_hab)):
        restricciones.append(((v1, v2), no_adyacentes))

    for v1, v2 in itertools.combinations(variables_gen, 2):
        restricciones.append(((v1, v2), no_adyacentes))

    variables_lab = [v for v in variables if v.startswith("lab")]
    variables_dep = [v for v in variables if v.startswith("dep")]
    variables_lab_y_dep = variables_lab + variables_dep

    def tiene_adyacente_en_lista(lista1, lista2):
        for celda in lista1:
            fila, columna = celda
            adyacentes = [
                (fila - 1, columna),
                (fila + 1, columna),
                (fila, columna - 1),
                (fila, columna + 1),
            ]
            if any(adyacente in lista2 for adyacente in adyacentes):
                return True

        return False

    def tiene_depositos_adyacentes(variables, valores):
        posiciones_lab = [pos for var, pos in zip(variables, valores) if var.startswith("lab")]
        posiciones_dep = [pos for var, pos in zip(variables, valores) if var.startswith("dep")]
        return tiene_adyacente_en_lista(posiciones_lab, posiciones_dep)

    if variables_lab and variables_dep:
        for lab in variables_lab:
            restricciones.append((tuple([lab] + variables_dep), tiene_depositos_adyacentes))

    def tiene_adyacente_libre(lista1, lista2, lista3):
        for celda in lista1:
            fila, columna = celda
            adyacentes = [
                (fila - 1, columna),
                (fila + 1, columna),
                (fila, columna - 1),
                (fila, columna + 1),
            ]
            filas, columnas = camp_size
            tiene_libre = any(
                0 <= nf < filas and 0 <= nc < columnas
                and (nf, nc) not in lista2 and (nf, nc) not in lista3
                for nf, nc in adyacentes
            )
            if not tiene_libre:
                return False
        return True

    def tiene_algun_adyacente_libre(variables, valores):
        posiciones_hab = [pos for var, pos in zip(variables, valores) if var.startswith("hab")]
        posiciones_resto = [pos for var, pos in zip(variables, valores) if not var.startswith("hab")]
        return tiene_adyacente_libre(posiciones_hab, posiciones_resto, craters)

    restricciones.append((tuple(variables), tiene_algun_adyacente_libre))

    problem = CspProblem(variables, dominios, restricciones)

    result = backtrack(problem, variable_heuristic=MOST_CONSTRAINED_VARIABLE,
                       value_heuristic=LEAST_CONSTRAINING_VALUE,
                       inference=True)
    if result is None:
        return None

    solucion = [
        (variable.split("_")[0], fila, columna)
        for variable, (fila, columna) in result.items()
    ]
    return solucion

def main():
    resultado = build_camp(
        camp_size=(5, 6),
        habs=2,
        generators=1,
        labs=1,
        deposits=2,
        airlocks=1,
        craters=[(2, 2), (2, 3)],
    )

    return resultado



if __name__ == "__main__":
    print(main())






