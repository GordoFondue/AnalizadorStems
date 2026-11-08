import os
import pytest
import sys
sys.path.insert(0, r"C:\Users\bryan\Downloads\proyectoPatrones\proyectoPatrones")
import numpy as np
from unittest.mock import patch, MagicMock
from modulos.analizador import AnalizadorPercusion
from modulos.otros import AnalizadorOtros
from modulos.bajo import AnalizadorBajo
from modulos.voz import AnalizadorVoz



@pytest.fixture
def audio_prueba():
    sr = 22050
    duracion = 1.0
    t = np.linspace(0, duracion, int(sr * duracion), endpoint=False)
    y_falso = 0.5 * np.sin(2 * np.pi * 440 * t)
    return y_falso, sr

def test_percusion(audio_prueba):
    y, sr = audio_prueba

    with patch("librosa.load", return_value=(y, sr)):
        analizador = AnalizadorPercusion("stem_bateria_falso.wav")
        bpm, tiempos = analizador.bpmYgolpes()
        assert isinstance(bpm, (int, float, np.number))
        assert bpm >= 0
        assert isinstance(tiempos, (list, np.ndarray))

        secuencia = analizador.secuencia_temporal(ventana_segundos=10)
        assert isinstance(secuencia, list)

        if len(secuencia) > 0:
            assert len(secuencia[0] == 2)
            assert isinstance(secuencia[0][0], (int, float, np.number))

def test_bajo(audio_prueba):
    y, sr = audio_prueba

    with patch("librosa.load", return_value=(y, sr)):
        analizador = AnalizadorBajo("stem_bajo_falso.wav")
        secuencia = analizador.secuencia_temporal(ventana_segundos=10)
        assert isinstance(secuencia, list)
        if len(secuencia) > 0:
            assert len(secuencia[0] == 2)

def test_voz(audio_prueba):
    y, sr = audio_prueba
    
    with patch("librosa.load", return_value=(y, sr)):
        analizador = AnalizadorVoz("stem_voz_falso.wav")
        secuencia = analizador.secuencia_temporal(ventana_segundos=10)
        assert isinstance(secuencia, list)
        if len(secuencia) > 0:
            assert len(secuencia[0] == 2)
def test_otros(audio_prueba):
    y, sr = audio_prueba
        
    with patch("librosa.load", return_value=(y, sr)):
        analizador = AnalizadorOtros("stem_voz_falso.wav")
        secuencia = analizador.secuencia_temporal(ventana_segundos=10)
        assert isinstance(secuencia, list)
        if len(secuencia) > 0:
            assert len(secuencia[0] == 2)