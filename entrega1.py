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
        return muestras_cargadas == 0 and len(muestras_igneas_por_cargar) == 0 and len(muestras_sedimentarias_por_cargar) == 0 and bateria > 0

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

        if bateria >= 1:
            for df, dc in movimientos_posibles:
                acciones.append(("moverse", (f+df, c+dc)))

            acciones.append(("equipar", "termico"))
            acciones.append(("equipar", "percusion"))

            if muestras_cargadas == 2 or (muestras_cargadas == 1 and len(muestras_igneas_por_cargar) == 0 and len(muestras_sedimentarias_por_cargar) == 0):
                acciones.append(("depositar", None))

            if posicion_rover not in self.zonas_sombra:
                acciones.append(("recargar", None))

        if bateria >= 4:
            for df, dc in sobremarchas_posibles:
                acciones.append(("sobremarcha", (f+df, c+dc)))

        if bateria >= 3:
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
            bateria -= muestras_cargadas
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
        bateria, tipo_taladro, muestras_cargadas, muestras_igneas_por_cargar, muestras_sedimentarias_por_cargar, posicion_rover = state
        distancias = []
        if len(muestras_igneas_por_cargar)>0:
            for posicion in muestras_igneas_por_cargar:
                distancias.append(self.manhattan(posicion_rover, posicion))
        if len(muestras_sedimentarias_por_cargar) > 0:
            for posicion1 in muestras_sedimentarias_por_cargar:
                distancias.append(self.manhattan(posicion_rover, posicion1))
        if not distancias:
            return 0
        return min(distancias) + 2 * (len(muestras_igneas_por_cargar) + len(muestras_sedimentarias_por_cargar))+ (len(muestras_igneas_por_cargar) + len(muestras_sedimentarias_por_cargar))/2
#costo por llegar a la distancia mínima + costo por recolectar cada muestra + costo por depositar las muestras si siempre se depositan 2. No usamos la recarga
#en la estimación ya que no necesariamente se va a recargar el rover y tampoco el costo por equipar un taladro nuevo ya que puede llegar a seguir con el mismo.
    def manhattan(self, pos_rata, pos_comida):
        return abs(pos_rata[0] - pos_comida[0]) + abs(pos_rata[1] - pos_comida[1])


def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    problem = MarsRoverBusquedaProblem(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas,muestras_sedimentarias)
    result = astar(problem, graph_search=True, viewer=BaseViewer())
    if result is None:
        return []
    return [step[0] for step in result.path()[1:]]

def main():
    acciones = planear_rover((0, 0),20,[(0, 1), (0, 2)],[(1, 1), (1, 2)],[(2, 3)])
    print(acciones)

if __name__ == "__main__":
    main()
