class ClasificadorFactory:

    @staticmethod
    def crear(categoria):

        if categoria == "RECICLABLE":
            return CalculadoraReciclable()

        if categoria == "APROVECHABLE":
            return CalculadoraAprovechable()

        return None