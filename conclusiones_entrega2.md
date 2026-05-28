# Diferencias entre la solución de Gemini Pro Extendido y nuestra solución

Ambas soluciones coinciden en la formulación general del CSP: variables con nombres únicos por instancia (hab_0, gen_1, etc.), dominios filtrados desde el inicio para incorporar las restricciones de borde y cráteres, y backtracking sin heurísticas como método de resolución. La diferencia más notable en este aspecto es que la solución de la IA usa un diccionario auxiliar var_types para mapear cada variable a su tipo, mientras que la solución propia usa startswith directamente sobre el nombre. Ambos enfoques son válidos, aunque var_types es más robusto ante cambios de nomenclatura.

En cuanto a restricciones, las dos implementan las ocho reglas del enunciado de forma equivalente. La diferencia está en la restricción de superposición: la IA usa una única restricción global con len(set(vals)) == len(vals), mientras que la solución propia genera restricciones binarias para cada par de variables con itertools.combinations. La versión binaria permite a SimpleAI detectar superposiciones más temprano durante el backtracking, ya que puede evaluarla con solo dos variables asignadas, sin necesidad de que todas estén definidas.

En términos de legibilidad, la solución de la IA está mejor estructurada visualmente con secciones comentadas. La solución propia es más compacta(tiene menos líneas y menos comentarios). 

En cuanto a corrección y performance, nuestra solución pasó todos los tests muy rápidamente(en poco más de 6 segundos). En cambio, la solución de la IA pasó todos hasta el caso 9 en unos pocos segundos pero este último quedó alrededor de una hora y media sin pasar así que simplemente no continuamos con el resto de tests para esta solución.
