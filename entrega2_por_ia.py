from simpleai.search import CspProblem, backtrack


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size
    crater_set = set(craters)

    variables = []
    var_types = {}

    # Función auxiliar para registrar variables
    def add_vars(prefix, count):
        for i in range(count):
            var_name = f"{prefix}_{i}"
            variables.append(var_name)
            var_types[var_name] = prefix

    add_vars("hab", habs)
    add_vars("gen", generators)
    add_vars("lab", labs)
    add_vars("dep", deposits)
    add_vars("air", airlocks)

    # Si la lista de requerimientos está vacía, no hay nada que ubicar
    if not variables:
        return []

    # --------------------------------------------------------
    # 1. Definición de Dominios (Filtrado inicial)
    # --------------------------------------------------------
    domains = {}
    for var in variables:
        v_type = var_types[var]
        valid_positions = []
        for r in range(rows):
            for c in range(cols):
                # Restricción: Cráteres intransitables
                if (r, c) in crater_set:
                    continue

                is_edge = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)

                # Restricción: Habitacionales al interior
                if v_type == "hab" and is_edge:
                    continue

                # Restricción: Esclusas en el borde
                if v_type == "air" and not is_edge:
                    continue

                valid_positions.append((r, c))

        domains[var] = valid_positions

    # --------------------------------------------------------
    # 2. Funciones de Restricción
    # --------------------------------------------------------
    constraints = []

    def is_adjacent(pos1, pos2):
        # Adyacencia ortogonal (Distancia Manhattan == 1)
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    # Restricción: Sin superposición
    def no_overlap(vars, vals):
        return len(set(vals)) == len(vals)

    if len(variables) > 1:
        constraints.append((variables, no_overlap))

    # Restricción: Seguridad energética (Generador no adyacente a Habitacional)
    def no_adj_gen_hab(vars, vals):
        return not is_adjacent(vals[0], vals[1])

    gen_vars = [v for v in variables if var_types[v] == "gen"]
    hab_vars = [v for v in variables if var_types[v] == "hab"]
    for g in gen_vars:
        for h in hab_vars:
            constraints.append(([g, h], no_adj_gen_hab))

    # Restricción: Aislamiento entre generadores
    def no_adj_gen_gen(vars, vals):
        return not is_adjacent(vals[0], vals[1])

    for i in range(len(gen_vars)):
        for j in range(i + 1, len(gen_vars)):
            constraints.append(([gen_vars[i], gen_vars[j]], no_adj_gen_gen))

    # Restricción: Cadena de suministro científico (Lab adyacente a >= 1 depósito)
    lab_vars = [v for v in variables if var_types[v] == "lab"]
    dep_vars = [v for v in variables if var_types[v] == "dep"]

    def lab_needs_dep(vars, vals):
        lab_pos = vals[0]
        dep_positions = vals[1:]
        return any(is_adjacent(lab_pos, dep_pos) for dep_pos in dep_positions)

    for l in lab_vars:
        if not dep_vars:
            return None  # Falla inmediata: hay laboratorios pero 0 depósitos.
        constraints.append(([l] + dep_vars, lab_needs_dep))

    # Restricción: Ruta de evacuación (Hab con >= 1 celda adyacente libre)
    def hab_evacuation(vars, vals):
        hab_pos = vals[0]
        other_positions = set(vals[1:])
        r, c = hab_pos

        neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        for nr, nc in neighbors:
            # Si el vecino está dentro del mapa...
            if 0 <= nr < rows and 0 <= nc < cols:
                # ...y no es un cráter, y tampoco está ocupado por otro módulo.
                if (nr, nc) not in crater_set and (nr, nc) not in other_positions:
                    return True
        return False

    for h in hab_vars:
        other_vars = [v for v in variables if v != h]
        constraints.append(([h] + other_vars, hab_evacuation))

    # --------------------------------------------------------
    # 3. Resolución del CSP
    # --------------------------------------------------------
    problem = CspProblem(variables, domains, constraints)
    result = backtrack(problem)

    if result is None:
        return None

    # --------------------------------------------------------
    # 4. Formateo del resultado
    # --------------------------------------------------------
    output = []
    for var, pos in result.items():
        output.append((var_types[var], pos[0], pos[1]))

    return output

if __name__ == "__main__":
    # Datos de ejemplo de la consigna
    resultado = build_camp(
        camp_size=(5, 6),
        habs=2,
        generators=1,
        labs=1,
        deposits=2,
        airlocks=1,
        craters=[(2, 2), (2, 3)],
    )

    if resultado:
        print("Distribución del campamento encontrada:")
        for modulo in resultado:
            print(modulo)
    else:
        print("No se encontró una solución válida para estas restricciones.")

