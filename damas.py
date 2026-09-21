"""Juego de Damas para dos jugadores usando pygame.

Reglas implementadas: tablero 8x8, movimiento diagonal, captura obligatoria,
capturas multiples, coronacion y victoria por falta de fichas o movimientos.
Los jugadores se identifican por sus colores: rojo y marfil.
"""

import sys
import random
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame


# Configuracion visual.
BOARD_SIZE = 640
PANEL_WIDTH = 240
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE
CELL_SIZE = BOARD_SIZE // 8
PANEL_X = BOARD_SIZE

LIGHT_SQUARE = (238, 222, 190)
DARK_SQUARE = (110, 72, 48)
BOARD_BORDER = (45, 31, 23)
BACKGROUND = (29, 32, 36)
PANEL_TEXT = (244, 240, 231)
ACCENT = (246, 194, 72)
BUTTON = (53, 59, 66)
BUTTON_HOVER = (72, 80, 89)
OVERLAY = (12, 15, 18, 220)
VALID_MOVE = (92, 183, 112)
CAPTURE_MOVE = (218, 87, 75)
RED = (190, 49, 48)
RED_HIGHLIGHT = (238, 92, 83)
IVORY = (225, 214, 181)
IVORY_HIGHLIGHT = (255, 241, 198)

Position = Tuple[int, int]


@dataclass
class Ficha:
    """Una ficha perteneciente a un jugador."""

    jugador: int
    coronada: bool = False


class Tablero:
    """Contiene el estado y las reglas, sin depender de pygame."""

    def __init__(self) -> None:
        self.casillas: List[List[Optional[Ficha]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.reiniciar()

    def reiniciar(self) -> None:
        """Crea la posicion inicial de una partida."""
        for fila in range(8):
            for columna in range(8):
                self.casillas[fila][columna] = None

        for fila in range(3):
            for columna in range(8):
                if self.es_jugable((fila, columna)):
                    self.casillas[fila][columna] = Ficha(2)

        for fila in range(5, 8):
            for columna in range(8):
                if self.es_jugable((fila, columna)):
                    self.casillas[fila][columna] = Ficha(1)

    def clonar(self) -> "Tablero":
        """Crea una copia independiente para analizar jugadas de la IA."""
        copia = Tablero.__new__(Tablero)
        copia.casillas = deepcopy(self.casillas)
        return copia

    @staticmethod
    def es_jugable(posicion: Position) -> bool:
        fila, columna = posicion
        return (fila + columna) % 2 == 1

    @staticmethod
    def dentro(posicion: Position) -> bool:
        fila, columna = posicion
        return 0 <= fila < 8 and 0 <= columna < 8

    def direcciones(self, ficha: Ficha) -> List[Tuple[int, int]]:
        """Devuelve las diagonales permitidas para mover/capturar."""
        if ficha.coronada:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        avance = -1 if ficha.jugador == 1 else 1
        return [(avance, -1), (avance, 1)]

    def movimientos_de_ficha(
        self, origen: Position, solo_capturas: bool = False
    ) -> List[Tuple[Position, Optional[Position]]]:
        """Lista destinos como (destino, ficha_capturada)."""
        ficha = self.casillas[origen[0]][origen[1]]
        if ficha is None:
            return []

        movimientos: List[Tuple[Position, Optional[Position]]] = []
        for df, dc in self.direcciones(ficha):
            intermedia = (origen[0] + df, origen[1] + dc)
            destino = (origen[0] + 2 * df, origen[1] + 2 * dc)

            if (
                self.dentro(destino)
                and self.dentro(intermedia)
                and self.casillas[intermedia[0]][intermedia[1]] is not None
                and self.casillas[intermedia[0]][intermedia[1]].jugador
                != ficha.jugador
                and self.casillas[destino[0]][destino[1]] is None
            ):
                movimientos.append((destino, intermedia))
            elif not solo_capturas and self.dentro(intermedia):
                if self.casillas[intermedia[0]][intermedia[1]] is None:
                    movimientos.append((intermedia, None))
        return movimientos

    def movimientos_legales(
        self, jugador: int, origen_fijo: Optional[Position] = None
    ) -> Dict[Position, List[Tuple[Position, Optional[Position]]]]:
        """Devuelve movimientos legales, aplicando la captura obligatoria."""
        posiciones = [origen_fijo] if origen_fijo is not None else [
            (fila, columna)
            for fila in range(8)
            for columna in range(8)
            if self.casillas[fila][columna] is not None
            and self.casillas[fila][columna].jugador == jugador
        ]
        capturas: Dict[Position, List[Tuple[Position, Optional[Position]]]] = {}
        for posicion in posiciones:
            if posicion is None:
                continue
            ficha = self.casillas[posicion[0]][posicion[1]]
            if ficha is not None and ficha.jugador == jugador:
                opciones = self.movimientos_de_ficha(posicion, solo_capturas=True)
                if opciones:
                    capturas[posicion] = opciones

        if capturas:
            return capturas

        if origen_fijo is not None:
            return {}
        normales: Dict[Position, List[Tuple[Position, Optional[Position]]]] = {}
        for posicion in posiciones:
            if posicion is None:
                continue
            ficha = self.casillas[posicion[0]][posicion[1]]
            if ficha is not None and ficha.jugador == jugador:
                opciones = self.movimientos_de_ficha(posicion)
                if opciones:
                    normales[posicion] = opciones
        return normales

    def mover(
        self, origen: Position, destino: Position, capturada: Optional[Position]
    ) -> bool:
        """Ejecuta un movimiento ya validado y corona si corresponde."""
        ficha = self.casillas[origen[0]][origen[1]]
        if ficha is None or self.casillas[destino[0]][destino[1]] is not None:
            return False
        self.casillas[origen[0]][origen[1]] = None
        self.casillas[destino[0]][destino[1]] = ficha
        if capturada is not None:
            self.casillas[capturada[0]][capturada[1]] = None

        if (ficha.jugador == 1 and destino[0] == 0) or (
            ficha.jugador == 2 and destino[0] == 7
        ):
            ficha.coronada = True
        return True

    def tiene_fichas(self, jugador: int) -> bool:
        return any(
            ficha is not None and ficha.jugador == jugador
            for fila in self.casillas
            for ficha in fila
        )

    def ganador(self, jugador_actual: int) -> Optional[int]:
        """Indica el ganador cuando el jugador actual ya no puede continuar."""
        if not self.tiene_fichas(jugador_actual) or not self.movimientos_legales(jugador_actual):
            return 3 - jugador_actual
        return None


class InteligenciaArtificial:
    """Oponente sin red: casual es aleatorio y experto evalua varias jugadas."""

    def elegir(
        self,
        tablero: Tablero,
        dificultad: str,
        origen_fijo: Optional[Position] = None,
    ) -> Optional[Tuple[Position, Position]]:
        opciones = tablero.movimientos_legales(2, origen_fijo)
        candidatos = [
            (origen, destino, capturada)
            for origen, movimientos in opciones.items()
            for destino, capturada in movimientos
        ]
        if not candidatos:
            return None
        if dificultad == "casual":
            origen, destino, _ = random.choice(candidatos)
            return origen, destino

        puntuados = []
        for origen, destino, capturada in candidatos:
            prueba = tablero.clonar()
            prueba.mover(origen, destino, capturada)
            puntuacion = self.evaluar(prueba)
            respuestas = prueba.movimientos_legales(1)
            if respuestas:
                peor_respuesta = float("inf")
                for respuesta_origen, movimientos in respuestas.items():
                    for respuesta_destino, respuesta_capturada in movimientos:
                        respuesta = prueba.clonar()
                        respuesta.mover(respuesta_origen, respuesta_destino, respuesta_capturada)
                        peor_respuesta = min(peor_respuesta, self.evaluar(respuesta))
                puntuacion = puntuacion * 0.45 + peor_respuesta * 0.55
            if capturada is not None:
                puntuacion += 35
            ficha = prueba.casillas[destino[0]][destino[1]]
            if ficha is not None and ficha.coronada:
                puntuacion += 60
            puntuados.append((puntuacion + random.random() * 4, origen, destino))
        _, origen, destino = max(puntuados)
        return origen, destino

    def evaluar(self, tablero: Tablero) -> float:
        valor = 0.0
        for fila in range(8):
            for columna in range(8):
                ficha = tablero.casillas[fila][columna]
                if ficha is None:
                    continue
                base = 150 if ficha.coronada else 100
                avance = fila if ficha.jugador == 2 else 7 - fila
                centralidad = 4 - abs(3.5 - columna)
                valor += (base + avance * 3 + centralidad) * (1 if ficha.jugador == 2 else -1)
        valor += len(tablero.movimientos_legales(2)) * 2
        valor -= len(tablero.movimientos_legales(1)) * 2
        return valor


class Juego:
    """Gestiona modos, turnos, popup de final y renderizacion."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Damas - Dos jugadores o contra IA")
        self.pantalla = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("arial", 16)
        self.fuente_grande = pygame.font.SysFont("arial", 26, bold=True)
        self.fuente_titulo = pygame.font.SysFont("arial", 34, bold=True)
        self.tablero = Tablero()
        self.ia = InteligenciaArtificial()
        self.modo = "2 jugadores"
        self.dificultad = "casual"
        self.reiniciar()

    def reiniciar(self) -> None:
        self.tablero.reiniciar()
        self.jugador_actual = 1
        self.seleccion: Optional[Position] = None
        self.movimientos_seleccionados: List[Tuple[Position, Optional[Position]]] = []
        self.ganador_actual: Optional[int] = None
        self.animacion: Optional[Dict[str, object]] = None
        self.duracion_animacion = 230

    def nombre_jugador(self, jugador: int) -> str:
        return "Rojo" if jugador == 1 else "Marfil"

    def color_jugador(self, jugador: int) -> Tuple[int, int, int]:
        return RED_HIGHLIGHT if jugador == 1 else IVORY_HIGHLIGHT

    def posicion_desde_pixel(self, pixel: Tuple[int, int]) -> Optional[Position]:
        x, y = pixel
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return y // CELL_SIZE, x // CELL_SIZE
        return None

    def rect_boton(self, fila: int) -> pygame.Rect:
        return pygame.Rect(BOARD_SIZE + 16, fila, PANEL_WIDTH - 32, 31)

    def seleccionar(self, posicion: Position) -> None:
        if self.animacion is not None:
            return
        opciones = self.tablero.movimientos_legales(self.jugador_actual)
        if posicion in opciones:
            self.seleccion = posicion
            self.movimientos_seleccionados = opciones[posicion]
        else:
            self.seleccion = None
            self.movimientos_seleccionados = []

    def realizar_movimiento(self, destino: Position) -> None:
        if self.seleccion is None or self.animacion is not None:
            return
        elegido = next(
            (capturada for posicion, capturada in self.movimientos_seleccionados
             if posicion == destino),
            None,
        )
        if not any(posicion == destino for posicion, _ in self.movimientos_seleccionados):
            return

        origen = self.seleccion
        self.seleccion = None
        self.movimientos_seleccionados = []
        self.iniciar_animacion(origen, destino, elegido, self.jugador_actual)

    def iniciar_animacion(
        self,
        origen: Position,
        destino: Position,
        capturada: Optional[Position],
        jugador: int,
    ) -> None:
        """Congela la partida y prepara el desplazamiento visual de una ficha."""
        ficha = self.tablero.casillas[origen[0]][origen[1]]
        if ficha is None:
            return
        self.animacion = {
            "origen": origen,
            "destino": destino,
            "capturada": capturada,
            "jugador": jugador,
            "ficha": ficha,
            "inicio": pygame.time.get_ticks(),
        }

    def finalizar_animacion(self) -> None:
        """Aplica el movimiento al terminar la animación y cambia el turno."""
        if self.animacion is None:
            return
        animacion = self.animacion
        self.animacion = None
        origen = animacion["origen"]
        destino = animacion["destino"]
        capturada = animacion["capturada"]
        jugador = animacion["jugador"]
        ficha = animacion["ficha"]
        if not isinstance(origen, tuple) or not isinstance(destino, tuple):
            return
        era_coronada = ficha.coronada if isinstance(ficha, Ficha) else False
        hubo_captura = capturada is not None
        self.tablero.mover(origen, destino, capturada)

        if hubo_captura and isinstance(ficha, Ficha) and (era_coronada or not ficha.coronada):
            siguientes = self.tablero.movimientos_legales(jugador, destino)
            if siguientes:
                if jugador == 1:
                    self.seleccion = destino
                    self.movimientos_seleccionados = siguientes[destino]
                else:
                    self.ejecutar_ia(destino)
                return

        self.seleccion = None
        self.movimientos_seleccionados = []
        self.jugador_actual = 3 - jugador
        self.ganador_actual = self.tablero.ganador(self.jugador_actual)
        if self.ganador_actual is None and self.modo == "vs IA" and self.jugador_actual == 2:
            self.ejecutar_ia()

    def actualizar_animacion(self) -> None:
        if self.animacion is None:
            return
        inicio = self.animacion["inicio"]
        if isinstance(inicio, int) and pygame.time.get_ticks() - inicio >= self.duracion_animacion:
            self.finalizar_animacion()

    def ejecutar_ia(self, origen_captura: Optional[Position] = None) -> None:
        """Prepara una única jugada de IA; el turno queda congelado durante ella."""
        if self.animacion is not None or self.modo != "vs IA" or self.jugador_actual != 2:
            return
        jugada = self.ia.elegir(self.tablero, self.dificultad, origen_captura)
        if jugada is None:
            self.ganador_actual = 1
            return
        origen, destino = jugada
        opciones = self.tablero.movimientos_legales(2, origen).get(origen, [])
        capturada = next((pieza for posicion, pieza in opciones if posicion == destino), None)
        self.iniciar_animacion(origen, destino, capturada, 2)

    def cambiar_modo(self, modo: str) -> None:
        self.modo = modo
        self.reiniciar()

    def manejar_panel(self, posicion: Tuple[int, int]) -> bool:
        if self.animacion is not None:
            return False
        if self.rect_boton(174).collidepoint(posicion):
            self.cambiar_modo("2 jugadores")
            return True
        if self.rect_boton(210).collidepoint(posicion):
            self.cambiar_modo("vs IA")
            return True
        if self.rect_boton(246).collidepoint(posicion) and self.modo == "vs IA":
            self.dificultad = "experto" if self.dificultad == "casual" else "casual"
            self.reiniciar()
            return True
        if self.rect_boton(282).collidepoint(posicion):
            self.reiniciar()
            return True
        return False

    def manejar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.KEYDOWN:
            if self.animacion is not None:
                return True
            if evento.key == pygame.K_ESCAPE:
                return False
            if evento.key == pygame.K_r:
                self.reiniciar()
            return True
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.animacion is not None:
                return True
            if evento.button == 3:
                self.seleccion = None
                self.movimientos_seleccionados = []
                return True
            if evento.button != 1:
                return True
            if self.ganador_actual is not None:
                if self.popup_boton("salir", evento.pos):
                    return False
                if self.popup_boton("reiniciar", evento.pos):
                    self.reiniciar()
                    return True
                if self.popup_boton("modo", evento.pos):
                    self.cambiar_modo("2 jugadores" if self.modo == "vs IA" else "vs IA")
                    return True
                return True
            if self.manejar_panel(evento.pos):
                return True
            if self.modo == "vs IA" and self.jugador_actual == 2:
                return True
            posicion = self.posicion_desde_pixel(evento.pos)
            if posicion is not None:
                if self.seleccion is not None and any(
                    destino == posicion for destino, _ in self.movimientos_seleccionados
                ):
                    self.realizar_movimiento(posicion)
                else:
                    self.seleccionar(posicion)
        return True

    def dibujar(self) -> None:
        self.pantalla.fill(BACKGROUND)
        for fila in range(8):
            for columna in range(8):
                color = LIGHT_SQUARE if (fila + columna) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.pantalla, color,
                                 (columna * CELL_SIZE, fila * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        movimientos_turno = self.tablero.movimientos_legales(self.jugador_actual)
        captura_obligatoria = any(
            capturada is not None
            for movimientos in movimientos_turno.values()
            for _, capturada in movimientos
        )
        if captura_obligatoria:
            for fila, columna in movimientos_turno:
                pygame.draw.rect(
                    self.pantalla, CAPTURE_MOVE,
                    (columna * CELL_SIZE + 7, fila * CELL_SIZE + 7,
                     CELL_SIZE - 14, CELL_SIZE - 14), 3,
                )

        if self.seleccion is not None:
            fila, columna = self.seleccion
            pygame.draw.rect(self.pantalla, ACCENT,
                             (columna * CELL_SIZE + 4, fila * CELL_SIZE + 4,
                              CELL_SIZE - 8, CELL_SIZE - 8), 5)
        for destino, capturada in self.movimientos_seleccionados:
            fila, columna = destino
            pygame.draw.circle(self.pantalla, CAPTURE_MOVE if capturada else VALID_MOVE,
                               (columna * CELL_SIZE + CELL_SIZE // 2,
                                fila * CELL_SIZE + CELL_SIZE // 2), 11)
        for fila in range(8):
            for columna in range(8):
                ficha = self.tablero.casillas[fila][columna]
                if ficha is not None and not self.es_origen_animado((fila, columna)):
                    self.dibujar_ficha(fila, columna, ficha)

        self.dibujar_ficha_animada()

        pygame.draw.rect(self.pantalla, BOARD_BORDER, (0, 0, BOARD_SIZE, BOARD_SIZE), 4)
        self.dibujar_panel()
        if self.ganador_actual is not None:
            self.dibujar_popup()
        pygame.display.flip()

    def es_origen_animado(self, posicion: Position) -> bool:
        return self.animacion is not None and self.animacion["origen"] == posicion

    def dibujar_ficha_animada(self) -> None:
        if self.animacion is None:
            return
        origen = self.animacion["origen"]
        destino = self.animacion["destino"]
        ficha = self.animacion["ficha"]
        inicio = self.animacion["inicio"]
        if not isinstance(origen, tuple) or not isinstance(destino, tuple):
            return
        transcurrido = pygame.time.get_ticks() - inicio
        progreso = min(1.0, max(0.0, transcurrido / self.duracion_animacion))
        # Suaviza el arranque y el frenado del desplazamiento.
        progreso = progreso * progreso * (3 - 2 * progreso)
        fila = origen[0] + (destino[0] - origen[0]) * progreso
        columna = origen[1] + (destino[1] - origen[1]) * progreso
        self.dibujar_ficha_en_pixel(fila, columna, ficha)

    def dibujar_ficha(self, fila: int, columna: int, ficha: Ficha) -> None:
        self.dibujar_ficha_en_pixel(fila, columna, ficha)

    def dibujar_ficha_en_pixel(self, fila: float, columna: float, ficha: Ficha) -> None:
        centro = (int(columna * CELL_SIZE + CELL_SIZE // 2),
                  int(fila * CELL_SIZE + CELL_SIZE // 2))
        color = RED if ficha.jugador == 1 else IVORY
        borde = RED_HIGHLIGHT if ficha.jugador == 1 else IVORY_HIGHLIGHT
        pygame.draw.circle(self.pantalla, (35, 26, 22), centro, 29)
        pygame.draw.circle(self.pantalla, color, centro, 25)
        pygame.draw.circle(self.pantalla, borde, centro, 25, 2)
        if ficha.coronada:
            corona = [(centro[0] - 13, centro[1] + 8), (centro[0] - 10, centro[1] - 10),
                      (centro[0] - 3, centro[1] - 2), (centro[0], centro[1] - 13),
                      (centro[0] + 4, centro[1] - 2), (centro[0] + 12, centro[1] - 10),
                      (centro[0] + 13, centro[1] + 8)]
            pygame.draw.polygon(self.pantalla, ACCENT, corona)
            pygame.draw.line(self.pantalla, (255, 232, 133),
                             (centro[0] - 13, centro[1] + 8),
                             (centro[0] + 13, centro[1] + 8), 3)

    def dibujar_icono(self, tipo: str, centro: Tuple[int, int]) -> None:
        x, y = centro
        if tipo == "izquierdo":
            pygame.draw.ellipse(self.pantalla, PANEL_TEXT, (x - 8, y - 10, 16, 20), 2)
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x, y - 7), (x, y - 2), 2)
            pygame.draw.circle(self.pantalla, VALID_MOVE, (x, y - 5), 2)
        elif tipo == "derecho":
            pygame.draw.ellipse(self.pantalla, PANEL_TEXT, (x - 8, y - 10, 16, 20), 2)
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x, y - 7), (x, y - 2), 2)
            pygame.draw.circle(self.pantalla, CAPTURE_MOVE, (x, y - 5), 2)
        elif tipo == "esc":
            pygame.draw.rect(self.pantalla, PANEL_TEXT, (x - 13, y - 8, 26, 16), 2, border_radius=3)
            etiqueta = self.fuente.render("ESC", True, PANEL_TEXT)
            self.pantalla.blit(etiqueta, etiqueta.get_rect(center=(x, y)))
        elif tipo == "r":
            pygame.draw.rect(self.pantalla, PANEL_TEXT, (x - 13, y - 8, 26, 16), 2, border_radius=3)
            etiqueta = self.fuente.render("R", True, PANEL_TEXT)
            self.pantalla.blit(etiqueta, etiqueta.get_rect(center=(x, y)))
        elif tipo == "flecha":
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x - 9, y), (x + 8, y), 2)
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x + 8, y), (x + 2, y - 6), 2)
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x + 8, y), (x + 2, y + 6), 2)
        elif tipo == "personas":
            pygame.draw.circle(self.pantalla, PANEL_TEXT, (x - 5, y - 4), 4, 2)
            pygame.draw.circle(self.pantalla, PANEL_TEXT, (x + 6, y - 4), 4, 2)
            pygame.draw.arc(self.pantalla, PANEL_TEXT, (x - 12, y + 1, 14, 12), 0, 3.14, 2)
            pygame.draw.arc(self.pantalla, PANEL_TEXT, (x - 1, y + 1, 14, 12), 0, 3.14, 2)
        elif tipo == "cerebro":
            pygame.draw.circle(self.pantalla, PANEL_TEXT, (x - 4, y), 7, 2)
            pygame.draw.circle(self.pantalla, PANEL_TEXT, (x + 5, y), 7, 2)
            pygame.draw.line(self.pantalla, PANEL_TEXT, (x, y - 8), (x, y + 8), 2)
        else:
            pygame.draw.circle(self.pantalla, PANEL_TEXT, centro, 8, 2)

    def dibujar_boton(self, rect: pygame.Rect, texto: str, icono: str) -> None:
        pygame.draw.rect(self.pantalla, BUTTON, rect, border_radius=5)
        self.dibujar_icono(icono, (rect.x + 17, rect.centery))
        self.pantalla.blit(self.fuente.render(texto, True, PANEL_TEXT), (rect.x + 32, rect.y + 7))

    def dibujar_panel(self) -> None:
        x = BOARD_SIZE + 18
        self.pantalla.blit(self.fuente_titulo.render("DAMAS", True, PANEL_TEXT), (x, 18))
        if self.ganador_actual is None:
            turno = f"Turno: {self.nombre_jugador(self.jugador_actual)}"
            turno_color = self.color_jugador(self.jugador_actual)
        else:
            turno = f"Gana: {self.nombre_jugador(self.ganador_actual)}"
            turno_color = self.color_jugador(self.ganador_actual)
        self.pantalla.blit(self.fuente_grande.render(turno, True, turno_color), (x, 68))
        modo = f"Modo: {self.modo}"
        self.pantalla.blit(self.fuente.render(modo, True, PANEL_TEXT), (x, 108))
        if self.modo == "vs IA":
            self.pantalla.blit(self.fuente.render(f"Nivel: {self.dificultad}", True, PANEL_TEXT), (x, 129))
        self.dibujar_boton(self.rect_boton(174), "2 jugadores", "personas")
        self.dibujar_boton(self.rect_boton(210), "vs IA", "cerebro")
        if self.modo == "vs IA":
            self.dibujar_boton(self.rect_boton(246), "Dificultad: " + self.dificultad, "ajuste")
        self.dibujar_boton(self.rect_boton(282), "Reiniciar", "flecha")
        instrucciones = [("izquierdo", "Seleccionar / mover"),
                 ("derecho", "Cancelar selección"),
                 ("esc", "Salir"), ("r", "Reiniciar")]
        for indice, (icono, texto) in enumerate(instrucciones):
            y = 342 + indice * 27
            self.dibujar_icono(icono, (x + 10, y + 8))
            self.pantalla.blit(self.fuente.render(texto, True, PANEL_TEXT), (x + 25, y))

    def popup_boton(self, boton: str, posicion: Tuple[int, int]) -> bool:
        centro_x, centro_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        rects = {"salir": pygame.Rect(centro_x - 135, centro_y + 50, 82, 36),
                 "reiniciar": pygame.Rect(centro_x - 41, centro_y + 50, 82, 36),
                 "modo": pygame.Rect(centro_x + 53, centro_y + 50, 82, 36)}
        return rects[boton].collidepoint(posicion)

    def dibujar_popup(self) -> None:
        capa = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        capa.fill(OVERLAY)
        self.pantalla.blit(capa, (0, 0))
        centro_x, centro_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        panel = pygame.Rect(centro_x - 180, centro_y - 105, 360, 210)
        pygame.draw.rect(self.pantalla, (38, 43, 49), panel, border_radius=10)
        titulo = self.fuente_titulo.render("Partida finalizada", True, PANEL_TEXT)
        mensaje = self.fuente_grande.render(f"Gana {self.nombre_jugador(self.ganador_actual)}", True,
                                             self.color_jugador(self.ganador_actual))
        self.pantalla.blit(titulo, titulo.get_rect(center=(centro_x, centro_y - 62)))
        self.pantalla.blit(mensaje, mensaje.get_rect(center=(centro_x, centro_y - 20)))
        rects = [("Salir", "salir"), ("Reiniciar", "reiniciar"), ("Cambiar modo", "modo")]
        for indice, (texto, _) in enumerate(rects):
            rect = pygame.Rect(centro_x - 135 + indice * 94, centro_y + 50, 82, 36)
            pygame.draw.rect(self.pantalla, BUTTON, rect, border_radius=5)
            etiqueta = self.fuente.render(texto, True, PANEL_TEXT)
            self.pantalla.blit(etiqueta, etiqueta.get_rect(center=rect.center))

    def ejecutar(self) -> None:
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                ejecutando = self.manejar_evento(evento)
                if not ejecutando:
                    break
            self.actualizar_animacion()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Juego().ejecutar()