import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
from PIL import Image

class Procesador:
    def __init__(self):
        self.model = None
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        self.activarTTS = False
        self.recognizer = sr.Recognizer()

    def darApiKey(self, apikey):
        genai.configure(api_key=apikey)
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    def activarVoz(self):
        self.activarTTS = True

    def desactivarVoz(self):
        self.activarTTS = False

    def _hablar(self, texto):
        if self.activarTTS == True:
            self.tts.say(texto)
            self.tts.runAndWait()

    def clasificarImagen(self, rutaImagen):
        if self.model == None:
            return "Error", "API KEY no establecida"

        try:
            imagen = Image.open(rutaImagen)
            prompt = "Identifica el objeto de esta imagen y clasificalo en UNA de estas 4 categorias: RECICLABLE, NO_RECICLABLE, APROVECHABLE, INFECCIOSO. Responde ESTRICTAMENTE en este formato: 'Nombre del objeto - CATEGORIA'. No agregues nada mas."
            
            respuesta = self.model.generate_content([prompt, imagen])
            resultado = respuesta.text.strip()
            
            if " - " in resultado:
                datos = resultado.split(" - ")
                nombreObjeto = datos[0].strip()
                categoriaObjeto = datos[1].strip()
                
                self._hablar("Residuo detectado y clasificado")
                return nombreObjeto, categoriaObjeto
            else:
                return "Error", "Formato incorrecto de la IA: " + resultado
                
        except Exception as e:
            return "Error", "Fallo al procesar la imagen: " + str(e)

    def escucharMicrofono(self):
        try:
            with sr.Microphone() as source:
                print("[Escuchando...]")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                texto = self.recognizer.recognize_google(audio, language="es-BO")
                return texto
        except sr.UnknownValueError:
            return "ERROR_AUDIO"
        except sr.RequestError:
            return "ERROR_CONEXION"
        except sr.WaitTimeoutError:
            return "ERROR_TIEMPO"

    def clasificarPorVoz(self):
        self._hablar("Que residuo vas a botar")
        textoUsuario = self.escucharMicrofono()
        
        if textoUsuario == "ERROR_AUDIO" or textoUsuario == "ERROR_CONEXION" or textoUsuario == "ERROR_TIEMPO":
            self._hablar("No te escuche bien o hubo un error")
            return "Error", "Problema con el microfono"

        prompt = "El usuario tiene este residuo: " + textoUsuario + ". Identifica el objeto y clasificalo en UNA de estas 4 categorias: RECICLABLE, NO_RECICLABLE, APROVECHABLE, INFECCIOSO. Responde ESTRICTAMENTE en este formato: 'Nombre del objeto - CATEGORIA'. No agregues nada mas."
        
        try:
            respuesta = self.model.generate_content(prompt)
            resultado = respuesta.text.strip()
            
            if " - " in resultado:
                datos = resultado.split(" - ")
                nombreObjeto = datos[0].strip()
                categoriaObjeto = datos[1].strip()
                
                self._hablar("Residuo clasificado por voz")
                return nombreObjeto, categoriaObjeto
            else:
                return "Error", "Formato incorrecto de la IA: " + resultado
                
        except Exception as e:
            return "Error", "Fallo al contactar a la IA: " + str(e)

    def resumirTexto(self, texto):
        prompt = "Resume en pocas palabras el siguiente texto: " + texto
        try:
            respuesta = self.model.generate_content(prompt)
            return respuesta.text.strip()
        except Exception as e:
            return "Error: " + str(e)