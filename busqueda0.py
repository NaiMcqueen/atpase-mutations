# -*- coding: utf-8 -*-
"""Busqueda0

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11K5V-I-MJn-Av0TCK8FFXLKeC2v6jU9s
"""

!pip install biopython
!pip install pandas

from Bio import Entrez, Medline
import pandas as pd
import re
import time

# Configuración
Entrez.email = "tu_email@ejemplo.com"  # Reemplaza con tu email
Entrez.api_key = "TU_API_KEY_AQUI"     # Reemplaza con tu API key

MAX_ARTICULOS = 3
ESPERA_SEGUNDOS = 0.1

keywords = [
    "ATPase mutations", "ATP synthase mutations", "P-ATPase mutations",
    "F-ATPase mutations", "V-ATPase mutations", "Natural ATPase variants",
    "Clinical ATPase mutations", "Disease-associated ATPase mutations"
]

# Función de búsqueda
def buscar_pubmed(termino, max_articulos=MAX_ARTICULOS):
    handle = Entrez.esearch(db="pubmed", term=termino, retmax=max_articulos)
    record = Entrez.read(handle)
    ids = record["IdList"]
    time.sleep(ESPERA_SEGUNDOS)
    return ids

# Función para obtener detalles
def obtener_detalles(ids):
    handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="text")
    records = Medline.parse(handle)
    time.sleep(ESPERA_SEGUNDOS)
    return list(records)

# Detectar mutaciones
def extraer_mutaciones(texto):
    patron = r"p\.\w{3}\d+\w{3}"
    return re.findall(patron, texto)

# Detectar gen
def detectar_gen(texto):
    posibles = re.findall(r"ATP\w{2,}", texto.upper())
    return posibles[0] if posibles else ""

# Detectar tipo ATPasa
def detectar_tipo_atpasa(texto):
    texto = texto.lower()
    if "v-atpase" in texto or "v type" in texto: return "V"
    if "p-atpase" in texto or "p type" in texto: return "P"
    if "f-atpase" in texto or "f type" in texto: return "F"
    if "atp synthase" in texto: return "F₀F₁"
    return ""

# Detectar subunidad
def detectar_subunidad(texto):
    match = re.search(r"subunit\s+([A-Z])", texto)
    return match.group(1) if match else ""

# Enfermedad asociada (lista mínima de términos comunes)
def detectar_enfermedad(texto):
    enfermedades = ["Parkinson", "epilepsy", "cancer", "diabetes", "Alzheimer", "Wilson", "dystonia"]
    for enf in enfermedades:
        if enf.lower() in texto.lower():
            return enf
    return ""

# Efecto funcional
def detectar_efecto_funcional(texto):
    patrones = ["loss of function", "gain of function", "impairs", "disrupt", "enhances", "reduces", "abolishes"]
    for p in patrones:
        if p in texto.lower():
            return p
    return ""

# Script principal
tabla = []

for keyword in keywords:
    print(f"\n🔍 Buscando: {keyword}")
    ids = buscar_pubmed(keyword)
    detalles = obtener_detalles(ids)

    for art in detalles:
        abstracto = art.get("AB", "")
        titulo = art.get("TI", "")
        texto = titulo + " " + abstracto
        mutaciones = extraer_mutaciones(texto)

        if mutaciones:
            for mut in mutaciones:
                posicion = re.findall(r"\d+", mut)
                entrada = {
                    "Gen": detectar_gen(texto),
                    "Proteína": detectar_gen(texto),  # Por ahora igual que el gen
                    "Tipo ATPasa": detectar_tipo_atpasa(texto),
                    "Subunidad": detectar_subunidad(texto),
                    "Mutación": mut,
                    "Posición": posicion[0] if posicion else "",
                    "Tipo": "clínica" if "disease" in texto.lower() or "clinical" in texto.lower() else "natural",
                    "Fuente": "PubMed",
                    "Enfermedad asociada": detectar_enfermedad(texto),
                    "Efecto funcional": detectar_efecto_funcional(texto),
                    "Estructura disponible (PDB/AlphaFold)": "",  # Lo implementamos después
                    "Paper": art.get("AU", [""])[0] + " (" + art.get("DP", "ND") + ")"
                }
                tabla.append(entrada)

# Guardar CSV
df = pd.DataFrame(tabla)
df.to_csv("mutaciones_atpasa.csv", index=False)
print("✅ Archivo 'mutaciones_atpasa.csv' guardado con éxito.")