import pygame 
import random 
from enum import Enum
from collections import namedtuple
import numpy as np

#Inicializo pygame
pygame.init()

#Cosas que cambian del proyecto para poder utilizar la IA

#Constantes de la ventana y el tamaño del bloque
BLOQUE_TAMANO = 20
ANCHO_VENTANA = 800
ALTO_VENTANA = 800
VELOCIDAD = 240

#Fuente de la letra
fuenteLetra = pygame.font.Font(None, 25)

#Color de la ventana
BLANCO = (255,255,255)
NEGRO = (0,0,0)
VERDE = (0,255,0)
VERDE2 = (10,200,10)
ROJO = (255,0,0)

#Direcciones
class Direccion(Enum):
    DERECHA = 1
    IZQUIERDA = 2
    ARRIBA = 3
    ABAJO = 4

#Contra errores de tipeo
Coordenada = namedtuple("Coordenada", 'x, y')


class SnakeGameIa:

    def __init__(self,ANCHO_VENTANA,ALTO_VENTANA):
        
        self.ANCHO_VENTANA = ANCHO_VENTANA
        self.ALTO_VENTANA = ALTO_VENTANA

        #Inicializamos la ventana con los tamaños ANCHOVENTANA, ALTO_VENTANA
        self.display = pygame.display.set_mode((self.ANCHO_VENTANA,self.ALTO_VENTANA))
        pygame.display.set_caption("Snake Game IA")
        self.clock = pygame.time.Clock()
        self.reiniciar()
        

    def reiniciar(self):

        #Inicio la serpiente para que vaya hacia la derecha y defino su bloque que cambiara la direccion(cabeza) y el cuerpo con el tamaño definido
        self.direccion = Direccion.DERECHA
        self.cabeza = Coordenada(self.ANCHO_VENTANA/2,self.ALTO_VENTANA/2)
        self.serpiente = [self.cabeza , Coordenada( (self.cabeza.x - BLOQUE_TAMANO) , (self.cabeza.y)),
        Coordenada(self.cabeza.x - (2 * BLOQUE_TAMANO) , self.cabeza.y)]

        #Incialimos la puntuación
        self.puntaje = 0
        #Inicializamos la manzana
        self.manzana = None
        #Utilizamos funcion para poner la manzana en una posicion al azar
        self.generarManzana()
        #Inicializamos las iteraciones de la pantalla
        self.iteraciones_pantalla = 0

    def generarManzana(self):

        #Generamos la manzana en una coordenada al azar
        #Con random.randint(a,b) que devuelve un numero entero entre a y b
        x = random.randint(0, (self.ANCHO_VENTANA-BLOQUE_TAMANO)//BLOQUE_TAMANO)*BLOQUE_TAMANO
        y = random.randint(0, (self.ALTO_VENTANA-BLOQUE_TAMANO)//BLOQUE_TAMANO)*BLOQUE_TAMANO
        #La manzana es una coordenada
        self.manzana = Coordenada(x,y)
        #Si la manzana esta en la coordenada de la serpiente la volvemos a generar 
        if self.manzana in self.serpiente:
            #Llamamos a la funcion recursivamente
            self.generarManzana()

    def actualizar(self,accion):

        #Aumentar las iteraciones de la pantalla 
        self.iteraciones_pantalla += 1
        #Coleccionar los inputs del usuario
        for evento in pygame.event.get():
            #Si el usuario apreta la X de la ventana se cierra
            if evento.type == pygame.QUIT:
                #Cerramos pygame y el programa
                pygame.quit()
                quit()
                    
        #Mover la serpiente con dichos inputs y cambiar la direccion de la cabeza
        self.movimientoSerpiente(accion) 
        #Actualzamos la cabeza de la serpiente
        self.serpiente.insert(0, self.cabeza)

        #Revisamo si hay colision (Game Over)
        recompensa = 0
        #Si la serpiente colisiona con la pared o con su cuerpo
        game_over = False
        
        if self.colision() or self.iteraciones_pantalla > 100*len(self.serpiente):
            #Reiniciamos el juego
            game_over = True
            recompensa = -10
            return recompensa, game_over, self.puntaje
        

        #Generar una nueva manzana si la serpiente come una Si la cabeza de la serpiente esta en la misma coordenada que la manzana
        if self.cabeza == self.manzana:
            #Aumentamos el puntaje
            self.puntaje += 1
            recompensa = 30
            #Generamos una nueva manzana
            self.generarManzana()
        #Si no comio manzana, removemos la cola de la serpiente
        else:
            #Removemos la cola de la serpiente
            self.serpiente.pop()

        #Actualizamos la pantalla
        self.actualizarPantalla()
        #Actualizamos la velocidad de la pantalla
        self.clock.tick(VELOCIDAD)

        #Retornamos la recompensa, si el juego termino y el puntaje
        return recompensa, game_over , self.puntaje
        
        
    ##Funcion que dibuja la serpiente y la manzana
    def actualizarPantalla(self):
        #Dibujamos el fondo de la pantalla
        self.display.fill(NEGRO)        
        
        for punto in self.serpiente:            
            pygame.draw.rect(self.display, VERDE , pygame.Rect(punto.x,punto.y,BLOQUE_TAMANO,BLOQUE_TAMANO))
            ##Efecto
            pygame.draw.rect(self.display, VERDE2 , pygame.Rect(punto.x + 2 , punto.y + 2 ,15 ,15))

        ##Funcion de pygame que dibuja pasandole como argumento (pantalla,color,forma(coordenadas))
        pygame.draw.rect(self.display,ROJO,pygame.Rect(self.manzana.x,self.manzana.y,BLOQUE_TAMANO,BLOQUE_TAMANO))

        #Texto Puntaje
        textoPuntiacion = fuenteLetra.render("Puntaje: "+ str(self.puntaje), True, BLANCO)
        self.display.blit(textoPuntiacion, [0,0])
        pygame.display.flip()
    
    ##Dependiendo de la accion pasada por parametro tomaremos la nueva direccion
    def movimientoSerpiente(self, accion):
        ##        [SEGUIR_DIRECCION_ACTUAL , Girar_DERECHA , Girar_IZQUIERDA]
        ## ACCION         [1,0,0]          ,    [0,1,0]    ,     [0,0,1]

        #Definimos el sentido horario
        sentidoHorario = [Direccion.DERECHA , Direccion.ABAJO , Direccion.IZQUIERDA , Direccion.ARRIBA]

        #Obtenemos el indice de la direccion actual
        indiceDireccionActual = sentidoHorario.index(self.direccion)
        if np.array_equal(accion,[1,0,0]):
            nuevaDireccion = sentidoHorario[indiceDireccionActual] #no cambia la direccion

        elif np.array_equal(accion,[0,1,0]): # giro derecha yendo a la derecha -> abajo -> izquierda -> arriba
            nuevoIndice = (indiceDireccionActual + 1) % 4 #Usas cuatro para que al sumar uno se vuelve a 0
            nuevaDireccion = sentidoHorario[nuevoIndice]

        else: # [0,0,1]  giro izquierda yendo a la derecha -> arriba -> izquierda -> abajo
            nuevoIndice = (indiceDireccionActual - 1) % 4 #Usas cuatro para que al sumar uno se vuelve a 0
            nuevaDireccion = sentidoHorario[nuevoIndice]

        #Cambiamos la direccion de la serpiente
        self.direccion = nuevaDireccion

        x = self.cabeza.x
        y = self.cabeza.y
        if self.direccion == Direccion.DERECHA:
            x += BLOQUE_TAMANO
        elif self.direccion == Direccion.IZQUIERDA:
            x -= BLOQUE_TAMANO
        elif self.direccion == Direccion.ARRIBA:
            y -= BLOQUE_TAMANO
        elif self.direccion == Direccion.ABAJO: # se suma porque arranca la ventana desde arriba con valor 0 y a medida que bajas se hace > 0
            y += BLOQUE_TAMANO
        
        #Actualizamos la cabeza
        self.cabeza = Coordenada(x,y)

    ##Funcion que revisa si la serpiente colisiona con algo
    def colision(self, punto = None):
        #Cambiamos la cabeza por un punto que arranca en la cabeza
        if punto == None:
            punto = self.cabeza
        #Si la cabeza conlisiona con la pared
        if punto.x > (self.ANCHO_VENTANA - BLOQUE_TAMANO) or punto.x < 0 or 0 > punto.y or punto.y > (self.ALTO_VENTANA - BLOQUE_TAMANO):
            return True
        #si colisiona con el cuerpo pero sin contar la cabeza
        if punto in self.serpiente[1:]:
            return True

        return False


