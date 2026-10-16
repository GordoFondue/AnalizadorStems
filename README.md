# Analizador de Stems Musicales

Este es un proyecto enfocado en separar y analizar los patrones de una canción. Básicamente, el programa agarra un archivo `.mp3`, lo divide en cuatro pistas separadas (batería, voz, bajo y otros) usando Demucs, y luego extrae información matemática de cada instrumento con Librosa.

La idea principal es agarrar los ritmos y las frecuencias, y pasarlos por un Modelo de Mezcla Gaussiana (GMM). Esto convierte los datos de la canción en una secuencia de letras (texto) para poder clasificar sus patrones más fácil. Al final, todo se guarda en una base de datos local.

### ¿Qué herramientas usa?
* **Python** como lenguaje principal.
* **PyQt6** para la interfaz gráfica.
* **Demucs** para separar las pistas de audio.
* **Librosa** para sacar los BPM, la energía, cruces por cero, etc.
* **Scikit-learn** para la parte de machine learning (clustering).
* **SQLite** para guardar los registros de las canciones analizadas.

### Instalación
Si quieres correr el código fuente, necesitas instalar las dependencias. Abre tu terminal y ejecuta:

`pip install pyqt6 librosa scikit-learn demucs numpy matplotlib`

### Cómo probarlo
Solo tienes que clonar este repositorio, entrar a la carpeta y ejecutar el archivo principal:

`python main.py`

*(Nota: Si no quieres instalar nada de código ni dependencias, ve a la sección de **Releases** a la derecha y descarga el archivo `.zip` con el ejecutable `.exe` listo para usarse).*
