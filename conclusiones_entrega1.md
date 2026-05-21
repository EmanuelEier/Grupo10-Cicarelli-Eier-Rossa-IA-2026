# Diferencias entre la solución de Gemini Pro Extendido y nuestra solución

Nuestro estado inicial es igual, a excepción de que Gemini separó las filas y columnas en dos variables diferentes y nosotros las usamos en una tupla.

En la heurística estimamos el tiempo base asumiendo el escenario más rápido posible. Para esto, tuvimos en cuenta cada uno de los mínimos costos posibles futuros. En cambio, Gemini la hizo más simple teniendo en cuenta solo el viaje hacia la muestra no recolectada más cercana, el tiempo fijo de perforación requerido para extraer todas las rocas que siguen en el mapa (**2 minutos por cada una**) y el tiempo obligatorio para depositar en el suelo tanto las muestras que el rover ya lleva cargadas como las que aún le falta recolectar (**1 minuto por cada muestra**).

En cuanto a los tests, logramos pasar todos con algunas advertencias por exceso de tiempo. En cambio, Gemini no logró pasar los tests de los casos **4, 5, 8, 9, 10, 11 y 12**.

Por último, en cuanto al rendimiento general, el nuestro fue mejor debido a los tiempos de resolución y por haber pasado todos los tests. En cambio, Gemini tuvo un rendimiento inferior en estos aspectos.
