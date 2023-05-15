#importamos las librerias necesarias 
import matplotlib.pyplot as plt
from IPython import display

#Plotting live results
plt.ion()


def plot(puntaje,mediaPuntaje):

    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Entrenando')
    plt.xlabel('Numero de juegos')
    plt.ylabel('Puntaje')
    plt.plot(puntaje)
    plt.plot(mediaPuntaje)
    plt.ylim(ymin=0)
    plt.text(len(puntaje)-1, puntaje[-1], str(puntaje[-1]))
    plt.text(len(mediaPuntaje)-1, mediaPuntaje[-1], str(mediaPuntaje[-1]))
    plt.show(block= False)
    plt.pause(.1)
