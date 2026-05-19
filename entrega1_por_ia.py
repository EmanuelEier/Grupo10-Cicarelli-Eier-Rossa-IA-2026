import math
from simpleai.search import SearchProblem, astar


class AresRoverProblem(SearchProblem):
    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        self.zonas_sombra = set(zonas_sombra)

        # El estado debe ser inmutable (tuplas) para que SimpleAI pueda hashearlo en graph_search.
        # Estructura del estado:
        # (fila, columna, bateria, taladro_activo, carga_actual, igneas_pendientes, sedimentarias_pendientes)
        estado_inicial = (
            rover_inicio[0],
            rover_inicio[1],
            bateria_inicial,
            None,  # Sin taladro equipado inicialmente
            0,  # Carga inicial
            tuple(muestras_igneas),
            tuple(muestras_sedimentarias)
        )
        super().__init__(estado_inicial)

    def actions(self, state):
        r, c, bat, taladro, carga, igneas, sedis = state
        acciones = []

        # 1. Moverse (Cuesta 1 de batería)
        if bat >= 1:
            acciones.append(("moverse", (r + 1, c)))
            acciones.append(("moverse", (r - 1, c)))
            acciones.append(("moverse", (r, c + 1)))
            acciones.append(("moverse", (r, c - 1)))

            # 3. Equipar taladro (Cuesta 1 de batería)
            if taladro != "termico":
                acciones.append(("equipar", "termico"))
            if taladro != "percusion":
                acciones.append(("equipar", "percusion"))

            # 5. Depositar cápsula (Cuesta 1 de batería)
            # Solo si tiene 2 muestras, o si tiene 1 pero ya no quedan más en el mapa.
            if carga == 2 or (carga > 0 and len(igneas) == 0 and len(sedis) == 0):
                acciones.append(("depositar", None))

        # 2. Sobremarcha (Cuesta 4 de batería)
        if bat >= 4:
            acciones.append(("sobremarcha", (r + 2, c)))
            acciones.append(("sobremarcha", (r - 2, c)))
            acciones.append(("sobremarcha", (r, c + 2)))
            acciones.append(("sobremarcha", (r, c - 2)))

        # 4. Perforar y recolectar (Cuesta 3 de batería, requiere espacio en bodega)
        if bat >= 3 and carga < 2:
            if (r, c) in igneas and taladro == "termico":
                acciones.append(("recolectar", "ignea"))
            if (r, c) in sedis and taladro == "percusion":
                acciones.append(("recolectar", "sedimentaria"))

        # 6. Desplegar paneles solares (Restricción: No en zonas de sombra)
        if (r, c) not in self.zonas_sombra and bat < 20:
            acciones.append(("recargar", None))

        return acciones

    def result(self, state, action):
        r, c, bat, taladro, carga, igneas, sedis = state
        tipo, param = action

        if tipo == "moverse":
            return (param[0], param[1], bat - 1, taladro, carga, igneas, sedis)
        elif tipo == "sobremarcha":
            return (param[0], param[1], bat - 4, taladro, carga, igneas, sedis)
        elif tipo == "equipar":
            return (r, c, bat - 1, param, carga, igneas, sedis)
        elif tipo == "recolectar":
            nuevas_igneas = tuple(m for m in igneas if m != (r, c)) if param == "ignea" else igneas
            nuevas_sedis = tuple(m for m in sedis if m != (r, c)) if param == "sedimentaria" else sedis
            return (r, c, bat - 3, taladro, carga + 1, nuevas_igneas, nuevas_sedis)
        elif tipo == "depositar":
            return (r, c, bat - 1, taladro, 0, igneas, sedis)
        elif tipo == "recargar":
            return (r, c, min(20, bat + 10), taladro, carga, igneas, sedis)

    def cost(self, state, action, state2):
        # La función de costo evalúa el TIEMPO, no la batería.
        tipo, param = action
        if tipo == "moverse":
            return 1
        elif tipo == "sobremarcha":
            return 1
        elif tipo == "equipar":
            return 3
        elif tipo == "recolectar":
            return 2
        elif tipo == "depositar":
            return 1 * state[4]  # 1 minuto por muestra de la carga actual
        elif tipo == "recargar":
            return 4

    def is_goal(self, state):
        _, _, _, _, carga, igneas, sedis = state
        # El objetivo se cumple cuando no quedan muestras en el mapa ni en la bodega.
        return len(igneas) == 0 and len(sedis) == 0 and carga == 0

    def heuristic(self, state):
        r, c, _, _, carga, igneas, sedis = state
        pendientes_en_mapa = len(igneas) + len(sedis)
        total_a_procesar = pendientes_en_mapa + carga

        if total_a_procesar == 0:
            return 0

        h = 0
        if pendientes_en_mapa > 0:
            # Distancia Manhattan a la muestra más cercana
            min_dist = min(abs(mr - r) + abs(mc - c) for mr, mc in igneas + sedis)
            # Como la sobremarcha avanza 2 celdas en 1 minuto, el tiempo mínimo de viaje es dist/2
            h += math.ceil(min_dist / 2)

        # Tiempo mínimo indispensable para recolectar las que quedan (2 min c/u)
        h += pendientes_en_mapa * 2

        # Tiempo mínimo indispensable para depositar todas las que faltan (1 min c/u)
        h += total_a_procesar * 1

        return h


def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    problema = AresRoverProblem(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)
    # Graph search es fundamental acá para no re-evaluar estados idénticos y quedar en loops
    resultado = astar(problema, graph_search=True)

    acciones = []
    if resultado:
        for accion, _ in resultado.path():
            if accion is not None:
                acciones.append(accion)
    return acciones


# Bloque de prueba de la consigna
if __name__ == '__main__':
    acciones = planear_rover(
        rover_inicio=(0, 0),
        bateria_inicial=20,
        zonas_sombra=[(0, 1), (0, 2)],
        muestras_igneas=[(1, 1), (1, 2)],
        muestras_sedimentarias=[(2, 3)],
    )
    for a in acciones:
        print(a)