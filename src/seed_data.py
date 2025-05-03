#!/usr/bin/env python3
import os
import sys
import requests
import urllib3

# 1) Suprime warnings de SSL no verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2) Asegura que Python encuentre los módulos en src/
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, Planet, Character

# URLs de SWAPI
SWAPI_PLANETS = 'https://swapi.dev/api/planets/'
SWAPI_PEOPLE  = 'https://swapi.dev/api/people/'

def fetch_all(url):
    items = []
    while url:
        # Deshabilitamos la verificación SSL porque el certificado de swapi.dev está expirado
        r = requests.get(url, verify=False)
        r.raise_for_status()
        data = r.json()
        items.extend(data['results'])
        url = data.get('next')
    return items

def seed_planets():
    print("🌍 Seeding planets...")
    for p in fetch_all(SWAPI_PLANETS):
        planet = Planet(
            nombre    = p['name'],
            clima     = p['climate'],
            terreno   = p['terrain'],
            poblacion = p['population']
        )
        db.session.merge(planet)
    db.session.commit()
    print("✅ Planets seeded.")

def seed_characters():
    print("👤 Seeding characters...")
    for p in fetch_all(SWAPI_PEOPLE):
        # Trae el nombre del homeworld
        home = requests.get(p['homeworld'], verify=False).json().get('name')
        # Trae la especie si existe
        especie = None
        if p['species']:
            especie = requests.get(p['species'][0], verify=False).json().get('name')
        char = Character(
            nombre        = p['name'],
            especie       = especie,
            planeta_natal = home,
            descripcion   = None
        )
        db.session.merge(char)
    db.session.commit()
    print("✅ Characters seeded.")

if __name__ == '__main__':
    # Asegúrate de haber corrido: flask db upgrade
    with app.app_context():
        seed_planets()
        seed_characters()
        print("🎉 ¡Datos de SWAPI cargados en tu DB!")
