# Diferencias entre la solución de Gemini Pro Extendido con nuestra solución

## En cuanto al enfoque

### Nuestra solución

1. El estado inicial está conformado por la batería, el tipo de taladro, las muestras cargadas en el rover, las muestras ígneas por cargar, las muestras sedimentarias por cargar y la posición del rover. Las zonas de sombra, al no cambiar nunca, las dejamos como atributo de la clase del problema.

2. En la heurística estimamos el tiempo base asumiendo el escenario más rápido posible:
   - viajar usando únicamente la sobremarcha (mitad de la distancia Manhattan),
   - sumar los tiempos fijos de recolección,
   - calcular el tiempo de depósito por cada muestra total,
   - y contemplar el cambio de taladros solo si es estrictamente necesario.

   Por otro lado, calculamos el escenario que menos energía consume para esas mismas acciones. Si descubrimos que la batería útil (la actual menos uno, para respetar la regla de nunca llegar a cero) no es suficiente, calculamos el déficit de energía y le sumamos al tiempo final los 4 minutos por cada recarga que el rover estará obligado a hacer.

3. Logramos pasar todos los tests con algunas advertencias por exceso de tiempo.

4. Tuvimos mejor rendimiento debido a los tiempos de resolución y por haber pasado todos los tests.

---

### Solución de Gemini Pro Extendido

1. El estado inicial está conformado por:
   - fila del rover,
   - columna del rover,
   - batería,
   - taladro activo,
   - carga actual,
   - ígneas pendientes,
   - y sedimentarias pendientes.

   Las zonas de sombra las deja como atributo de la clase del problema.

2. La heurística la resolvió sumando tres costos de tiempo que son ineludibles:
   - el viaje hacia la muestra no recolectada más cercana (asumiendo el escenario ideal de moverse siempre usando sobremarcha a doble velocidad),
   - el tiempo fijo de perforación requerido para extraer todas las rocas que siguen en el mapa (2 minutos por cada una),
   - y el tiempo obligatorio para depositar en el suelo tanto las muestras que el rover ya lleva cargadas como las que aún le falta recolectar (1 minuto por cada muestra).

3. No logró pasar los tests de los casos 4, 5, 8, 9, 10, 11 y 12.

4. El rendimiento en cuanto a los tiempos de resolución y los tests fue inferior.
