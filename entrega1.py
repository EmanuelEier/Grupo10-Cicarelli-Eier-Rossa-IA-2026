import math
from math import ceil

from numpy.random import rand
from simpleai.search import SearchProblem, astar
from simpleai.search.viewers import BaseViewer


class MarsRoverBusquedaProblem(SearchProblem):
    def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
        self.zonas_sombra = tuple(zonas_sombra)

        bateria = bateria_inicial
        tipo_taladro = None
        muestras_cargadas = 0
        muestras_igneas_por_cargar = tuple(muestras_igneas)
        muestras_sedimentarias_por_cargar = tuple(muestras_sedimentarias)
        posicion_rover = rover_inicio

        inicial = (bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover)
        super(MarsRoverBusquedaProblem, self).__init__(inicial)

    def is_goal(self, state):
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover = state
        return muestras_cargadas == 0 and len(muestras_igneas_por_cargar) == 0 and len(muestras_sedimentarias_por_cargar) == 0

    def actions(self, state):
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover = state
        acciones = []
        movimientos_posibles = [
            (-1, 0),#Arriba
            (1, 0),#Abajo
            (0, 1),#Derecha
            (0, -1)#Izquierda
        ]

        sobremarchas_posibles = [
            (-2, 0),#Arriba x 2
            (2, 0),#Abajo x 2
            (0, 2),#Derecha x 2
            (0, -2)#Izquierda x 2
        ]
        f, c = posicion_rover

        if bateria > 1:
            for df, dc in movimientos_posibles:
                acciones.append(("moverse", (f+df, c+dc)))

            if tipo_taladro != "termico":
                acciones.append(("equipar", "termico"))
            if tipo_taladro != "percusion":
                acciones.append(("equipar", "percusion"))

            if muestras_cargadas == 2 or (muestras_cargadas == 1 and len(muestras_igneas_por_cargar) == 0 and len(muestras_sedimentarias_por_cargar) == 0):
                acciones.append(("depositar", None))

        if posicion_rover not in self.zonas_sombra and bateria < 20:
            acciones.append(("recargar", None))

        if bateria > 4:
            for df, dc in sobremarchas_posibles:
                acciones.append(("sobremarcha", (f+df, c+dc)))

        if bateria > 3:
            if 0 <= muestras_cargadas < 2:
                if posicion_rover in muestras_igneas_por_cargar and tipo_taladro == "termico":
                    acciones.append(("recolectar", "ignea"))
                elif posicion_rover in muestras_sedimentarias_por_cargar and tipo_taladro == "percusion":
                    acciones.append(("recolectar", "sedimentaria"))

        return acciones

    def result(self, state, action):
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover = state
        accion, parametro = action

        muestras_igneas_por_cargar_lista = list(muestras_igneas_por_cargar)
        muestras_sedimentarias_por_cargar_lista = list(muestras_sedimentarias_por_cargar)

        if accion == "moverse":
            bateria -= 1
            posicion_rover = parametro
        elif accion == "sobremarcha":
            bateria -= 4
            posicion_rover = parametro
        elif accion == "equipar":
            tipo_taladro = parametro
            bateria -= 1
        elif accion == "recolectar":
            bateria -= 3
            muestras_cargadas += 1
            if parametro == "ignea":
                muestras_igneas_por_cargar_lista.remove(posicion_rover)
            else:
                muestras_sedimentarias_por_cargar_lista.remove(posicion_rover)
        elif accion == "depositar":
            bateria -= 1
            muestras_cargadas = 0
        else:
            if bateria <= 10:
                bateria += 10
            else:
                bateria = 20

        return (bateria, tipo_taladro, muestras_cargadas, tuple(muestras_igneas_por_cargar_lista), tuple(muestras_sedimentarias_por_cargar_lista), posicion_rover)

    def cost(self, state, action, state2):#Devuelve el tiempo que conlleva realizar cada acción
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover = state
        accion, parametro = action
        costo = 0
        if accion == "moverse" or accion == "sobremarcha":
            costo = 1
        elif accion == "depositar":
            costo = muestras_cargadas
        elif accion == "equipar":
            costo = 3
        elif accion == "recolectar":
            costo = 2
        else:
            costo = 4

        return costo

    def heuristic(self, state):
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas, muestras_sedimentarias, posicion = state

        faltantes = list(muestras_igneas) + list(muestras_sedimentarias)

        # Si ya no quedan en el mapa, solo falta depositar el inventario
        if not faltantes:
            if muestras_cargadas > 0:
                return muestras_cargadas
            return 0

        distancias = [self.manhattan(posicion, p) for p in faltantes]
        dist_min = min(distancias)

        # Calculamos el tiempo mínimo ideal
        # El movimiento más veloz es sobremarcha: 1 min cada 2 casillas.
        tiempo_mov = math.ceil(dist_min / 2.0)

        tiempo_rec = 2 * len(faltantes)
        muestras_a_depositar = len(faltantes) + muestras_cargadas
        tiempo_dep = muestras_a_depositar

        tiempo_eq = 0
        hay_igneas = len(muestras_igneas) > 0
        hay_sedimentarias = len(muestras_sedimentarias) > 0

        if hay_igneas and hay_sedimentarias:
            tiempo_eq = 3
        elif hay_igneas and tipo_taladro != "termico":
            tiempo_eq = 3
        elif hay_sedimentarias and tipo_taladro != "percusion":
            tiempo_eq = 3

        # Calculamos si será necesario recargar (batería es la limitante secundaria)
        bat_mov = dist_min  # El movimiento de menos batería consume 1 por casilla
        bat_rec = 3 * len(faltantes)
        bat_eq = 1 if tiempo_eq > 0 else 0
        bat_dep = math.ceil(muestras_a_depositar / 2.0)  # Entran 2 muestras por cápsula

        bat_necesaria = bat_mov + bat_rec + bat_eq + bat_dep

        # La batería NUNCA llega a 0, entonces la batería utilizable máxima actual es (bateria - 1)
        deficit = bat_necesaria - (bateria - 1)

        tiempo_recarga = 0
        if deficit > 0:#si se necesita recargar batería
            recargas = math.ceil(deficit / 10.0)#dividimos el deficit por 10(cantidad que se recarga en cada recarga) y redondeamos al entero superior
            tiempo_recarga = recargas * 4#cada recarga tarda 4 minutos

        return tiempo_mov + tiempo_rec + tiempo_dep + tiempo_eq + tiempo_recarga

    def manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    problem = MarsRoverBusquedaProblem(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas,muestras_sedimentarias)
    result = astar(problem, graph_search=True)
    if result is None:
        return []
    return [step[0] for step in result.path()[1:]]

def main():
    acciones = planear_rover((0, 0),20,[(0, 1), (0, 2)],[(1, 1), (1, 2)],[(2, 3)])
    print(acciones)

if __name__ == "__main__":
    main()
