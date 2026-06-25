from threading import Thread
from ChatConIA.cola import cola_imagenes

class Worker(Thread):

    def run(self):

        while True:

            imagen = cola_imagenes.get()

            print("Procesando:", imagen)

            cola_imagenes.task_done()