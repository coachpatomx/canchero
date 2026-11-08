"""Asegura que la raíz del proyecto esté en sys.path para importar
periodization_engine y app durante los tests."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
