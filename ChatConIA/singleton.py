from ChatConIA.procesador import Procesador

class ProcesadorSingleton:

    instancia = None

    @staticmethod
    def obtener():

        if ProcesadorSingleton.instancia is None:

            ProcesadorSingleton.instancia = Procesador()

        return ProcesadorSingleton.instancia