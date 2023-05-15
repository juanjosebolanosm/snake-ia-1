import numpy as np
import random
import torch
from collections import deque
from SnakeGameIA import SnakeGameIa, Direccion,Coordenada 
from modelo import AprendizajePorRefuerzoLinearQ, entrenamientoQ
from plot import plot


# Constantes 
MEMORIA_MAXIMA = 100_000
TAMANIO_BATCH = 1000
LR = 0.001

class Agente:

    def __init__(self):
        self.numerojuegos = 0
        self.epsilon = 0 # aleatoriedad
        self.gamma = 0.9 # taza de descuento
        self.memoria = deque(maxlen=MEMORIA_MAXIMA) # popIZQUIERDA()
        self.model = AprendizajePorRefuerzoLinearQ(11, 256, 3)
        self.trainer = entrenamientoQ(self.model, lr=LR, gamma=self.gamma)


    def obtener_estado(self, juego):
        cabeza = juego.serpiente[0]
        punto_izq = Coordenada(cabeza.x - 20, cabeza.y)
        punto_der = Coordenada(cabeza.x + 20, cabeza.y)
        punto_arr = Coordenada(cabeza.x, cabeza.y - 20)
        punto_abj = Coordenada(cabeza.x, cabeza.y + 20)
        
        dir_izq = juego.direccion == Direccion.IZQUIERDA
        dir_der = juego.direccion == Direccion.DERECHA
        dir_arr = juego.direccion == Direccion.ARRIBA
        dir_abj = juego.direccion == Direccion.ABAJO

        estado = [
            # Peligro hacia adelante
            (dir_der and juego.colision(punto_der)) or 
            (dir_izq and juego.colision(punto_izq)) or 
            (dir_arr and juego.colision(punto_arr)) or 
            (dir_abj and juego.colision(punto_abj)),

            # Peligro hacia la derecha
            (dir_arr and juego.colision(punto_der)) or 
            (dir_abj and juego.colision(punto_izq)) or 
            (dir_izq and juego.colision(punto_arr)) or 
            (dir_der and juego.colision(punto_abj)),

            # Peligro hacia la izquierda
            (dir_abj and juego.colision(punto_der)) or 
            (dir_arr and juego.colision(punto_izq)) or 
            (dir_der and juego.colision(punto_arr)) or 
            (dir_izq and juego.colision(punto_abj)),
            
            # Mover
            dir_izq,
            dir_der,
            dir_arr,
            dir_abj,
            
            # Ubicacion del alimento
            juego.manzana.x < juego.cabeza.x,  # food IZQUIERDA
            juego.manzana.x > juego.cabeza.x,  # food DERECHA
            juego.manzana.y < juego.cabeza.y,  # food AR
            juego.manzana.y > juego.cabeza.y  # food ABAJO
            ]

        return np.array(estado, dtype=int)

    def persistir(self, estado, accion, recompensa, siguiente_estado, max):
        self.memoria.append((estado, accion, recompensa, siguiente_estado, max)) # popIZQUIERDA si max es alcanzado

    def train_long_memory(self):
        if len(self.memoria) > TAMANIO_BATCH:
            muestra = random.sample(self.memoria, TAMANIO_BATCH) # list of tARles
        else:
            muestra = self.memoria

        estado, acciones, recompensas, siguiente_estado, max = zip(*muestra)
        self.trainer.pasoDeEentrenamiento(estado, acciones, recompensas, siguiente_estado, max)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.pasoDeEentrenamiento(state, action, reward, next_state, done)

    def train_short_memory(self, estado, accion, recompensa, siguiente_estado, max):
        self.trainer.pasoDeEentrenamiento(estado, accion, recompensa, siguiente_estado, max)

    def obtenerAccion(self, estado):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.numerojuegos
        mov_final = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            movimiento = random.randint(0, 2)
            mov_final[movimiento] = 1
        else:
            estado0 = torch.tensor(estado, dtype=torch.float)
            prediccion = self.model(estado0)
            movimiento = torch.argmax(prediccion).item()
            mov_final[movimiento] = 1

        return mov_final


def train():
    plot_puntaje = []
    plot_prom_puntaje = []
    puntaje_total = 0
    record = 0
    agent = Agente()
    juego = SnakeGameIa(ANCHO_VENTANA = 640, ALTO_VENTANA = 640)
    while True:
        # get old state
        estado_inicial = agent.obtener_estado(juego)

        # get move
        mov_final = agent.obtenerAccion(estado_inicial)

        # perform move and get new state
        recompensa, max, puntaje = juego.actualizar(mov_final)
        estado_nuevo = agent.obtener_estado(juego)

        # train short memory
        agent.train_short_memory(estado_inicial, mov_final, recompensa, estado_nuevo, max)

        # remember
        agent.persistir(estado_inicial, mov_final, recompensa, estado_nuevo, max)

        if max:
            # train long memory, plot result
            juego.reiniciar()
            agent.numerojuegos += 1
            agent.train_long_memory()

            if puntaje > record:
                record = puntaje
                agent.model.cargarModelo()

            print('Game', agent.numerojuegos, 'Score', puntaje, 'Record:', record)

            plot_puntaje.append(puntaje)
            puntaje_total += puntaje
            mean_score = puntaje_total / agent.numerojuegos
            plot_prom_puntaje.append(mean_score)
            plot(plot_puntaje, plot_prom_puntaje)


if __name__ == '__main__':
    train()