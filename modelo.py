#Librerias necesarias para el funcionamiento del modelo
#Torch -> Libreria de redes neuronales
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class AprendizajePorRefuerzoLinearQ(nn.Module):
    def __init__(self, inputTamano, ocultoTamano , salidaTamano):
        #Inicializamos la red neuronal
        super().__init__()
        #Capas de la red neuronal 
        self.linear1 = nn.Linear(inputTamano, ocultoTamano )
        self.linear2 = nn.Linear(ocultoTamano , salidaTamano)

    #Funcion de la red neuronal
    def forward(self, x):
        #Funcion de activacion de la red neuronal
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    #Funcion para cargar el modelo
    def cargarModelo(self, nombreArchivo ='modelo.pth'):
        #Cargamos el modelo si existe
        ruta = './modelo'
        if not os.path.exists(ruta):
            os.mkdir(ruta)
        
        nombreArchivo = os.path.join(ruta,nombreArchivo)
        torch.save(self.state_dict(), nombreArchivo)

#Clase para entrenar el modelo
class entrenamientoQ:
    def __init__(self, modelo, lr , gamma):
        self.modelo = modelo
        self.lr = lr
        self.gamma = gamma
        self.optimizador = optim.Adam(modelo.parameters(), lr = self.lr)
        self.criterio = nn.MSELoss()

    def pasoDeEentrenamiento(self,estado,accion,recompensa,proximoEstado, perder):
        
        #Convertimos los datos a tensores
        estado = torch.tensor(estado, dtype=torch.float)
        proximoEstado = torch.tensor(proximoEstado,dtype=torch.float)
        accion = torch.tensor(accion,dtype=torch.long)
        recompensa = torch.tensor(recompensa,dtype=torch.float)
       
        #Si el estado es un vector, lo convertimos en un tensor
        if len(estado.shape) == 1:
            #(1, x)
            estado = torch.unsqueeze(estado, 0)
            proximoEstado = torch.unsqueeze(proximoEstado, 0)
            accion = torch.unsqueeze(accion, 0)
            recompensa = torch.unsqueeze(recompensa, 0)
            perder = (perder, )

        #prediccion de la red neuronal
        predicion = self.modelo(estado)
        objetivo = predicion.clone()
        for i in range(len(perder)):
            nuevoQ = recompensa[i]
            if not perder[i]:
                nuevoQ = recompensa[i] + self.gamma * torch.max(self.modelo(proximoEstado[i]))

            objetivo[i][torch.argmax(accion[i]).item()]  = nuevoQ 

        # recompensa + gamma * maximo de la (predicioniccion Q) 
        #clonamos la predicion para tener los 3 valores
        #predicionicciones [argmax(accion)] = nuevoQ
        self.optimizador.zero_grad() #funcion pytorch
        perdida = self.criterio(objetivo , predicion)
        perdida.backward()
        self.optimizador.step()


