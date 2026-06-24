import re

class ParserClasificacion:

    @staticmethod
    def interpretar(texto):

        patron = r"^(.+)\s-\s(RECICLABLE|NO_RECICLABLE|APROVECHABLE|INFECCIOSO)$"

        coincidencia = re.match(
            patron,
            texto.strip()
        )

        if coincidencia:

            objeto = coincidencia.group(1)

            categoria = coincidencia.group(2)

            return objeto, categoria

        return None, None