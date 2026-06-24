import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import cv2

from PIL import Image
from .parser import ParserClasificacion


class Procesador:

    def __init__(self):

        self.model = None

        self.tts = pyttsx3.init()

        self.tts.setProperty(
            'rate',
            150
        )

        self.activarTTS = False

        self.recognizer = sr.Recognizer()

    def darApiKey(self, apikey):

        genai.configure(
            api_key=apikey
        )

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash"
        )

    def activarVoz(self):
        self.activarTTS = True

    def desactivarVoz(self):
        self.activarTTS = False

    def _hablar(self, texto):

        if self.activarTTS:

            self.tts.say(texto)

            self.tts.runAndWait()

    # ==========================
    # PROCESAMIENTO DE IMAGEN
    # ==========================

    def mejorarImagen(self, ruta):

        imagen = cv2.imread(ruta)

        if imagen is None:
            return

        gris = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2GRAY
        )

        cv2.imwrite(
            ruta,
            gris
        )

    # ==========================
    # CLASIFICAR IMAGEN
    # ==========================

    def clasificarImagen(self, rutaImagen):

        if self.model is None:

            return (
                "Error",
                "API KEY no establecida"
            )

        try:

            self.mejorarImagen(
                rutaImagen
            )

            imagen = Image.open(
                rutaImagen
            )

            prompt = """
            Identifica el objeto de esta imagen
            y clasifícalo en UNA de estas categorías:

            RECICLABLE
            NO_RECICLABLE
            APROVECHABLE
            INFECCIOSO

            Responde exactamente:

            Nombre del objeto - CATEGORIA
            """

            respuesta = self.model.generate_content(
                [prompt, imagen]
            )

            resultado = respuesta.text.strip()

            objeto, categoria = (
                ParserClasificacion.interpretar(
                    resultado
                )
            )

            if objeto is None:

                return (
                    "Error",
                    "Formato incorrecto: "
                    + resultado
                )

            self._hablar(
                "Residuo detectado y clasificado"
            )

            return (
                objeto,
                categoria
            )

        except Exception as e:

            return (
                "Error",
                "Fallo al procesar la imagen: "
                + str(e)
            )

    # ==========================
    # CONTAR OBJETOS
    # ==========================

    def contarObjetos(
        self,
        ruta_imagen,
        tipo_objeto="botellas"
    ):

        import re

        try:

            imagen = Image.open(
                ruta_imagen
            )

            prompt = f"""
            Cuenta cuántas
            {tipo_objeto}
            existen en la imagen.

            Responde SOLO
            con un número entero.
            """

            respuesta = self.model.generate_content(
                [prompt, imagen]
            )

            texto = respuesta.text.strip()

            numeros = re.findall(
                r'\d+',
                texto
            )

            if numeros:

                cantidad = int(
                    numeros[0]
                )

                return (
                    cantidad
                    if cantidad > 0
                    else 1
                )

            return 1

        except Exception as e:

            print(e)

            return 1