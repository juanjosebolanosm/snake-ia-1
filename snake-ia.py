import pygame 
import random 
from enum import Enum
from collections import namedtuple



#Inicializa el modulo pygame
pygame.init()

#Board size
board_width  = 800
board_height  = 800
#cada cuadricula sera de un tamaño de 10 por lo que se podran dar 80*60 
bloque_size = 40

#Defino la fuente de la letra "arial" y el tamaño de la letra "25
letra = pygame.font.SysFont('arial', 25)

#Colores 
BLANCO = (255,255,255)
NEGRO = (0,0,0)
VERDE = (0,255,0)
VERDE2 = (10,200,10)
ROJO = (255,0,0)

#Asigno valores a cada dirección
class Direccion(Enum):
    DERECHA = 1
    IZQUIERDA = 2
    ARRIBA = 3
    ABAJO = 4

#Coordenada 
Coordenada = namedtuple("Coordenada", 'x, y')

class SnakeGame:
    def __init__(self,board_width ,board_height ):

        self.board_width  = board_width 
        self.board_height  = board_height 

        #Iniciar el tablero 
        self.display = pygame.display.set_mode((self.board_width ,self.board_height ))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        #Iniciar Snake
        self.direccion = Direccion.DERECHA
        self.cabeza_serpiente = Coordenada(self.board_width /2,self.board_height /2)
        self.cuerpo_serpiente = [self.cabeza_serpiente , Coordenada( (self.cabeza_serpiente.x - bloque_size) , (self.cabeza_serpiente.y)),
        Coordenada(self.cabeza_serpiente.x - (2 * bloque_size) , self.cabeza_serpiente.y)]


        self.puntaje = 0

        #Inicializo la comida
        self.comida = None

        #Pongo comida en una posicion al azar
        self._generar_comida()

        #Velocidad del juego
        self.velocidad_clock = 8

    def _generar_comida(self):

        #Genero una coordenada al azar
        x = random.randint(0, (self.board_width -bloque_size)//bloque_size)*bloque_size
        y = random.randint(0, (self.board_height -bloque_size)//bloque_size)*bloque_size
        #Asigno la coordenada a la comida
        self.comida = Coordenada(x,y)

        #Si la comida esta en el cuerpo de la serpiente genero una nueva comida
        if self.comida in self.cuerpo_serpiente:
            self._generar_comida()

    def actualizar(self):
        
        #Ver si perdio 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                perder = True

            #Presionar una tecla para mover la serpiente
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and self.direccion != Direccion.DERECHA:
                    self.direccion = Direccion.IZQUIERDA
                elif evento.key == pygame.K_RIGHT and self.direccion != Direccion.IZQUIERDA:
                    self.direccion = Direccion.DERECHA
                elif evento.key == pygame.K_UP and self.direccion != Direccion.ABAJO:
                    self.direccion = Direccion.ARRIBA
                elif evento.key == pygame.K_DOWN and self.direccion != Direccion.ARRIBA:
                    self.direccion = Direccion.ABAJO

                    
        #Mover la serpiente
        self._mover_serpiente(self.direccion) 
        self.cuerpo_serpiente.insert(0, self.cabeza_serpiente)

        #Comprobar si perdio
        perder = False
        if self._colision():
            perder = True
            return perder, self.puntaje

        
        if self.cabeza_serpiente == self.comida:
            self.puntaje += 1
            self._generar_comida()
        else:
            self.cuerpo_serpiente.pop()

            
        #Aumentar velocidad del juego segun el puntaje
        if 10 > self.puntaje > 5 :
            self.velocidad_clock = 12
        elif 15 > self.puntaje > 10:
            self.velocidad_clock = 14
        elif 20 > self.puntaje > 15:
            self.velocidad_clock = 16
        elif self.puntaje > 30:
            self.velocidad_clock = 24
            

        #Actualizar tablero 
        self._actualizar_pantalla()
        self.clock.tick(self.velocidad_clock)

        return perder , self.puntaje
        
        
        
    
    def _actualizar_pantalla(self):
        self.display.fill(NEGRO)        
        for punto in self.cuerpo_serpiente:            
            pygame.draw.rect(self.display, VERDE , pygame.Rect(punto.x,punto.y,bloque_size,bloque_size))
            
            pygame.draw.rect(self.display, VERDE2 , pygame.Rect(punto.x + 4 , punto.y + 4 ,30 ,30))

        #funcion pygame.draw
        pygame.draw.rect(self.display,ROJO,pygame.Rect(self.comida.x,self.comida.y,bloque_size,bloque_size))


        texto_puntaje = letra.render(" Score: "+ str(self.puntaje), True, BLANCO)
        self.display.blit(texto_puntaje, [0,0])
        pygame.display.flip()
    
    #Cambios de dirección Snake
    def _mover_serpiente(self, direccion):
        x = self.cabeza_serpiente.x
        y = self.cabeza_serpiente.y
        if direccion == Direccion.DERECHA:
            x += bloque_size
        elif direccion == Direccion.IZQUIERDA:
            x -= bloque_size
        elif direccion == Direccion.ARRIBA:
            y -= bloque_size
        elif direccion == Direccion.ABAJO:
            y += bloque_size
        
        self.cabeza_serpiente = Coordenada(x,y)


    #Colisiones
    def _colision(self):

        #Sale del tablero
        if self.cabeza_serpiente.x > (board_width  - bloque_size) or self.cabeza_serpiente.x < 0 or 0 > self.cabeza_serpiente.y or self.cabeza_serpiente.y > (board_height  - bloque_size):
            return True
        
        #Colisiona con su cuerpo
        if self.cabeza_serpiente in self.cuerpo_serpiente[1:]:
            return True

        return False



if __name__ == '__main__':
    pardita = SnakeGame(board_width ,board_height )

    while True:
        perder, puntaje = pardita.actualizar()
        #Si perdio termina el juego
        if perder == True:
            break
            
    print("Su Score fue de: ", puntaje)
    pygame.quit()