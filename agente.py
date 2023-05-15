import numpy as np
import random, torch
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MEMORIA_MAXIMA = 100_000
TAMANIO_BATCH = 1000
LR = 0.001

class Agente:

    def __init__(self):
        self.numerojuegos = 0
        self.epsilon = 0 # aleatoriedad
        self.gamma = 0.9 # taza de descuento
        self.memoria = deque(maxlen=MEMORIA_MAXIMA) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def obtener_estado(self, juego):
        cabeza = juego.snake[0]
        punto_izq = Point(cabeza.x - 20, cabeza.y)
        punto_der = Point(cabeza.x + 20, cabeza.y)
        punto_arr = Point(cabeza.x, cabeza.y - 20)
        punto_abj = Point(cabeza.x, cabeza.y + 20)
        
        dir_izq = juego.direction == Direction.LEFT
        dir_der = juego.direction == Direction.RIGHT
        dir_arr = juego.direction == Direction.UP
        dir_abj = juego.direction == Direction.DOWN

        estado = [
            # Peligro hacia adelante
            (dir_der and juego.is_collision(punto_der)) or 
            (dir_izq and juego.is_collision(punto_izq)) or 
            (dir_arr and juego.is_collision(punto_arr)) or 
            (dir_abj and juego.is_collision(punto_abj)),

            # Peligro hacia la derecha
            (dir_arr and juego.is_collision(punto_der)) or 
            (dir_abj and juego.is_collision(punto_izq)) or 
            (dir_izq and juego.is_collision(punto_arr)) or 
            (dir_der and juego.is_collision(punto_abj)),

            # Peligro hacia la izquierda
            (dir_abj and juego.is_collision(punto_der)) or 
            (dir_arr and juego.is_collision(punto_izq)) or 
            (dir_der and juego.is_collision(punto_arr)) or 
            (dir_izq and juego.is_collision(punto_abj)),
            
            # Mover
            dir_izq,
            dir_der,
            dir_arr,
            dir_abj,
            
            # Ubicacion del alimento
            juego.manzana.x < juego.cabeza.x,  # food left
            juego.manzana.x > juego.cabeza.x,  # food right
            juego.manzana.y < juego.cabeza.y,  # food up
            juego.manzana.y > juego.cabeza.y  # food down
            ]

        return np.array(estado, dtype=int)

    def persistir(self, estado, accion, recompensa, siguiente_estado, max):
        self.memoria.append((estado, accion, recompensa, siguiente_estado, max)) # popleft si max es alcanzado

    def train_long_memory(self):
        if len(self.memoria) > TAMANIO_BATCH:
            muestra = random.sample(self.memoria, TAMANIO_BATCH) # list of tuples
        else:
            muestra = self.memoria

        estado, acciones, recompensas, siguiente_estado, max = zip(*muestra)
        self.trainer.train_step(estado, acciones, recompensas, siguiente_estado, max)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, estado, accion, recompensa, siguiente_estado, max):
        self.trainer.train_step(estado, accion, recompensa, siguiente_estado, max)

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
    juego = SnakeGameAI()
    while True:
        # get old state
        estado_inicial = agent.obtener_estado(juego)

        # get move
        mov_final = agent.obtenerAccion(estado_inicial)

        # perform move and get new state
        recompensa, max, puntaje = juego.play_step(mov_final)
        estado_nuevo = agent.obtener_estado(juego)

        # train short memory
        agent.train_short_memory(estado_inicial, mov_final, recompensa, estado_nuevo, max)

        # remember
        agent.persistir(estado_inicial, mov_final, recompensa, estado_nuevo, max)

        if max:
            # train long memory, plot result
            juego.reset()
            agent.numerojuegos += 1
            agent.train_long_memory()

            if puntaje > record:
                record = puntaje
                agent.model.save()

            print('Game', agent.numerojuegos, 'Score', puntaje, 'Record:', record)

            plot_puntaje.append(puntaje)
            puntaje_total += puntaje
            mean_score = puntaje_total / agent.numerojuegos
            plot_prom_puntaje.append(mean_score)
            plot(plot_puntaje, plot_prom_puntaje)


if __name__ == '__main__':
    train()