import itertools

from simpleai.search import CspProblem, backtrack, MOST_CONSTRAINED_VARIABLE, LEAST_CONSTRAINING_VALUE


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    variables = []
    # Variables: una por cada módulo a ubicar
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

    # Dominios: celdas válidas para cada variable (sin cráteres, respetando borde/interior)
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
    # Restricciones
    restricciones = []

    # Sin superposición
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

    # Generador no adyacente a habitacional
    for v1, v2 in itertools.product(tuple(variables_gen), tuple(variables_hab)):
        restricciones.append(((v1, v2), no_adyacentes))
    #, ni generadores entre sí
    for v1, v2 in itertools.combinations(variables_gen, 2):
        restricciones.append(((v1, v2), no_adyacentes))

    variables_lab = [v for v in variables if v.startswith("lab")]
    variables_dep = [v for v in variables if v.startswith("dep")]

    def tiene_depositos_adyacentes(variables, valores):
        fila, columna = valores[0]  # siempre el lab primero
        posiciones_dep = set(valores[1:])
        adyacentes = [
            (fila - 1, columna),
            (fila + 1, columna),
            (fila, columna - 1),
            (fila, columna + 1),
        ]
        return any(adyacente in posiciones_dep for adyacente in adyacentes)

    # Cada laboratorio debe tener al menos un depósito adyacente
    if variables_lab and variables_dep:
        for lab in variables_lab:
            restricciones.append((tuple([lab] + variables_dep), tiene_depositos_adyacentes))

    def tiene_algun_adyacente_libre(variables, valores):
        posicion_hab = valores[0]
        posiciones_resto = set(valores[1:])
        craters_set = set(craters)
        fila, columna = posicion_hab
        filas, columnas = camp_size
        adyacentes = [
            (fila - 1, columna),
            (fila + 1, columna),
            (fila, columna - 1),
            (fila, columna + 1),
        ]
        return any(
            0 <= nf < filas and 0 <= nc < columnas
            and (nf, nc) not in posiciones_resto and (nf, nc) not in craters_set
            for nf, nc in adyacentes
        )

    # Cada habitacional debe tener al menos una celda libre adyacente
    for hab in variables_hab:
        otras = [v for v in variables if v != hab]
        restricciones.append((tuple([hab] + otras), tiene_algun_adyacente_libre))

    problem = CspProblem(variables, dominios, restricciones)

    result = backtrack(problem)
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






