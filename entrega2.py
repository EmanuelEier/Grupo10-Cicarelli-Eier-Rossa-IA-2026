import itertools


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    variables = []

    for i in range(habs):
        variables.append("hab")

    for i in range(generators):
        variables.append("gen")

    for i in range(labs):
        variables.append("lab")

    for i in range(deposits):
        variables.append("dep")

    for i in range(airlocks):
        variables.append("air")

    dominios = {}

    def borde_mapa(fila, columna):
        return fila == camp_size[0] or fila == 0 or columna == camp_size[0] or columna == 0

    for variable in variables:
        dominios[variable] = []
        for fila in range(camp_size[0]):
            for columna in range(camp_size[1]):
                if (fila, columna) not in craters:
                    if variable == "air":
                        if borde_mapa(fila, columna):
                            dominios[variable].append((fila, columna))
                    elif variable == "hab":
                        if not borde_mapa(fila, columna):
                            dominios[variable].append((fila, columna))
                    else:
                        dominios[variable].append((fila, columna))

    restricciones = []

    def no_superposicion(pos1, pos2):
        return pos1 != pos2

    for v1, v2 in itertools.combinations(variables, 2)
        restricciones.append(((v1, v2), no_superposicion))

    variables_gen = [v for v in variables if v == "gen"]
    variables_hab = [v for v in variables if v == "hab"]

    def no_adyacentes(variables, valores):
        (f1, c1) = valores[0][0]
        (f2, c2) = valores[1][0]

        return not abs(f1 - f2) + abs(c1 - c2) == 1

    for v1, v2 in itertools.product(tuple(variables_gen), tuple(variables_hab)):
        restricciones.append(((v1, v2), no_adyacentes))

    for v1, v2 in itertools.combinations(variables_gen, 2)
        restricciones.append(((v1, v2), no_adyacentes))

    variables_lab = [v for v in variables if v == "lab"]
    variables_dep = [v for v in variables if v == "dep"]
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
        variables_lab = [v for v in variables if v == "lab"]
        variables_dep = [v for v in variables if v == "dep"]

        return tiene_adyacente_en_lista(variables_lab, variables_dep)

    restricciones.append((tuple(variables_lab_y_dep), tiene_depositos_adyacentes))

    def tiene_algun_adyacente_libre(variables, valores):
        variables_hab = [v for v in variables if v == "hab"]
        resto_de_variables = [v for v in variables if v != "hab"]

        return (not tiene_adyacente_en_lista(variables_hab, resto_de_variables)) and (
            not tiene_adyacente_en_lista(variables_hab, craters))

    restricciones.append((variables, tiene_algun_adyacente_libre))







