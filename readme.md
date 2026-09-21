# Juego de Damas con Pygame

Juego de Damas en 2D desarrollado en Python con `pygame`. Incluye partidas para dos jugadores, modo contra la IA, dificultad casual y experta, reglas de captura obligatoria, coronación, animaciones y detección del final de la partida.

## Ejecución

Instala la dependencia y ejecuta el juego con:

```bash
python -m pip install pygame
python damas.py
```

## Estructura del proyecto

- [`damas.py`](damas.py): código completo del juego.
- `readme.md`: documentación y registro del proceso de desarrollo.
- `.gitignore`: archivos y carpetas locales excluidos de Git.

## Prompts utilizados

### 1. Implementación inicial

> Crea un juego de Damas completamente funcional en Python que se pueda jugar en 2D.

#### Requisitos técnicos

- Usa `pygame` para la interfaz gráfica.
- El tablero debe ser de 8x8 con casillas alternadas, claras y oscuras.
- Las fichas deben diferenciarse visualmente por color, una para cada jugador.
- Implementa las reglas estándar de Damas: movimiento diagonal, captura de fichas enemigas y coronación al llegar al borde opuesto.
- Las fichas coronadas deben verse distintas, por ejemplo, mediante un símbolo o indicador visual.
- Permite alternar turnos entre dos jugadores humanos.
- Detecta automáticamente cuándo un jugador gana, ya sea porque el oponente se queda sin fichas o sin movimientos legales.

#### Nivel de completitud

Desarrolla una **implementación sólida** con:

- Validación completa de movimientos según las reglas estándar de Damas.
- Detección automática de capturas obligatorias.
- Detección del final de la partida, incluyendo victoria y derrota.
- Lógica de turnos clara y sin ambigüedades.

#### Interactividad

- Los jugadores deben poder seleccionar una ficha haciendo clic y ver sus movimientos válidos.
- Deben poder mover la ficha a una casilla válida mediante un clic.
- El juego debe validar los movimientos y capturar fichas automáticamente.
- Debe mostrar claramente de quién es el turno actual.

#### Estructura del código

- Organiza el código en clases, por ejemplo, `Tablero`, `Ficha` y `Juego`.
- Mantén la lógica del juego separada de la representación visual.
- Incluye una función para reiniciar el juego.

#### Salida

- Entrega un archivo `.py` completo y ejecutable.
- Incluye comentarios claros que expliquen las secciones principales.
- El juego debe iniciarse inmediatamente al ejecutar el script.

### 2. Mejoras visuales y modo contra la IA

> El juego debe incorporar los siguientes cambios y mejoras.

#### Mejoras visuales

- El icono de las fichas coronadas debe ser una corona, no una `K`.
- La finalización de la partida debe mostrar un popup con botones para salir, reiniciar o cambiar el modo de juego.
- El texto del turno debe utilizar el color de la ficha que juega actualmente.
- Implementa iconos para la información de los controles del menú derecho, como el clic derecho, `Esc` y `R`.

#### Cambios pendientes

- Implementa el modo contra la IA.
- Permite elegir la dificultad entre casual y experta.
- La dificultad experta no debe ser imposible, pero sí desafiante para el jugador humano.
- Permite cambiar el modo de juego desde el menú derecho en cualquier momento y agrega iconos a los botones.

### 3. Corrección del modo contra la IA

> El juego presenta un fallo crítico:

- El modo contra la IA es injugable: el jugador humano gana automáticamente al realizar el primer movimiento.
- Asegúrate de haber implementado una IA funcional.
- Realiza partidas de prueba contra la IA.
- Prueba comportamientos no deseados y corrígelos.

### 4. Animaciones y guía de capturas

> El juego debe incorporar los siguientes cambios y mejoras.

#### Mejoras visuales

- Las fichas deben tener una animación breve en la dirección seleccionada.
- La animación debe congelar el turno actual; cuando finalice, debe comenzar el siguiente turno.
- Los iconos de las teclas deben sustituir a los nombres de las teclas en el panel derecho.
- Cuando exista una captura obligatoria, la ficha o las fichas que deben jugarse deben aparecer resaltadas en el tablero para guiar al jugador.

## Explicación de los prompts

1. El primer prompt fue mejorado en [Prompt Cowboy](https://www.promptcowboy.ai/). Le pedí a Copilot que creara un juego de Damas sencillo en Python y allí agregué los requisitos detallados.
2. Algunas decisiones visuales no terminaban de convencerme, así que le pedí a la IA varias mejoras de calidad de vida. El modo contra la IA se incorporó en este segundo prompt.
3. El modo contra la IA no avanzaba después del primer turno y otorgaba una victoria automática al jugador humano. Se le pidió a Copilot que realizara pruebas y aplicara el refactor necesario para que la IA funcionara correctamente.
4. Se agregaron cambios visuales menores, como una animación sencilla para el movimiento de cada ficha y la señalización de las fichas que tienen capturas obligatorias.

## Pruebas humanas

Después de finalizar cada prompt, ejecuté el juego para probarlo personalmente. Así descubrí las fallas visuales, la ausencia inicial del modo contra la IA, el fallo del modo IA y la falta de animaciones antes del cuarto prompt.

## Reflexión final

La IA me parece una herramienta interesante para programar. Presenta una forma particular de crear código; sin embargo, todo el juego se programó en un solo archivo. Si se quisiera ampliar con más modos de juego y variantes culturales, podría volverse difícil localizar problemas y terminar generando código espagueti.

Lo que más me gustó de programar con IA fue la facilidad para delegar una tarea repetitiva, como crear la base del juego, y dejar las pruebas del lado humano. Aunque, por hacer este juego sencillo, Copilot consumió aproximadamente 60 000 tokens de contexto... Bueno, todo sea por la ciencia.

## Comprensión del código

Aunque el código está escrito en un lenguaje que conozco poco, comprendo que al inicio se definen las constantes y la configuración global. Después se define la clase `Ficha`, que diferencia el color de cada jugador y el estado de las fichas coronadas.

Luego se define la matriz de 8x8 donde se juega. El método `direcciones()` delimita las direcciones de movimiento de cada ficha; `movimientos_de_ficha()` calcula los desplazamientos diagonales y las capturas; y `movimientos_legales()` determina si existe una captura obligatoria y qué movimientos son válidos.

El método `mover()` actualiza la posición de la ficha en el tablero y la corona cuando corresponde. Después, `ganador()` comprueba las condiciones de victoria.

La IA se mueve aleatoriamente en el modo casual. En el modo experto utiliza `evaluar()` para asignar puntuaciones a las posiciones y escoger jugadas más convenientes.

La parte que menos comprendo es la representación visual, pero reconozco funciones como `reiniciar()`, que configura la ventana, las fuentes y la tasa de refresco. El punto de entrada instancia la clase `Juego` y ejecuta la aplicación.