#!/usr/bin/env python3
"""
scripts/consola_empresas.py
--------------------------
Consola interactiva de terminal con pandas para consultar y filtrar empresas
de la carga EDO 2026 de forma limpia, ordenada y rápida.

Permite:
- Búsqueda en tiempo real por RUC o Razón Social (parcial, sin distinguir mayúsculas/acentos).
- Filtrar por Región o Situación Institucional.
- Ver ficha técnica detallada de una empresa (todos sus contactos, teléfonos y enlaces).
- Abrir WhatsApp en el navegador directamente desde la terminal con un clic o comando.
- Acceso directo a una consola interactiva de Python con el DataFrame `df` listo.
"""

import os
import sys
import re
import unicodedata
from pathlib import Path
import pandas as pd

# Archivo de datos normalizados
CSV_PATH = Path(__file__).resolve().parent.parent / "carga_limpia_edo2026.csv"
EXCEL_PATH = Path(__file__).resolve().parent.parent / "AlvaVidalCarga.xlsx"

def quitar_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    ).lower()

def cargar_datos() -> pd.DataFrame:
    """Carga los datos limpios si existe el CSV; si no, ejecuta el script de limpieza."""
    if not CSV_PATH.exists():
        print(f"[*] Generando carga limpia desde '{EXCEL_PATH.name}'...")
        from cargar_excel_a_bitacora import procesar_excel
        df = procesar_excel(EXCEL_PATH)
        df.to_csv(CSV_PATH, index=False, encoding="utf-8")
    else:
        df = pd.read_csv(CSV_PATH, dtype={"ruc": str, "ubigeo": str, "ciiu": str, "contacto_principal_telefono": str, "contacto_alternativo_telefono": str})
    
    # Rellenar valores nulos
    df = df.fillna("")
    # Columna auxiliar normalizada para búsqueda rápida
    df["_busqueda"] = (df["ruc"].astype(str) + " " + df["razon_social"].apply(quitar_acentos) + " " + df["region"].apply(quitar_acentos))
    return df

def formatear_tabla(sub_df: pd.DataFrame, max_filas: int = 25):
    """Muestra una tabla compacta con alta densidad y alineación clara."""
    if sub_df.empty:
        print("\n\033[93m[!] No se encontraron empresas con ese criterio.\033[0m\n")
        return

    total = len(sub_df)
    muestra = sub_df.head(max_filas)

    print(f"\n\033[1;36mResultados encontrados: {total}\033[0m" + (f" (mostrando primeros {max_filas})" if total > max_filas else ""))
    print("-" * 125)
    print(f"{'#':<3} | {'RUC':<11} | {'RAZÓN SOCIAL':<32} | {'REGIÓN':<10} | {'TELÉFONO':<12} | {'SITUACIÓN':<25} | {'WHATSAPP'}")
    print("-" * 125)

    idx_global = 1
    for _, row in muestra.iterrows():
        razon = (row['razon_social'][:30] + "..") if len(row['razon_social']) > 32 else row['razon_social']
        tel = row['contacto_principal_telefono'] if row['contacto_principal_telefono'] else "-"
        sit = (row['situacion_empresa_descripcion'][:23] + "..") if len(row['situacion_empresa_descripcion']) > 25 else row['situacion_empresa_descripcion']
        tiene_wa = "\033[92mSí (wa)\033[0m" if row['wa_link'] else "\033[90m-\033[0m"

        print(f"{idx_global:<3} | {row['ruc']:<11} | {razon:<32} | {row['region']:<10} | {tel:<12} | {sit:<25} | {tiene_wa}")
        idx_global += 1
    print("-" * 125)
    print("\033[90mTip: Escribe el RUC para ver la ficha completa con todos los contactos.\033[0m\n")

def mostrar_detalle(empresa: pd.Series):
    """Muestra la ficha técnica completa y limpia de una empresa."""
    print("\n" + "=" * 80)
    print(f"\033[1;32mFICHA DE EMPRESA: {empresa['razon_social']}\033[0m")
    print("=" * 80)
    print(f"  RUC              : \033[1m{empresa['ruc']}\033[0m")
    print(f"  Región / Ubigeo  : {empresa['region']} (Ubigeo: {empresa['ubigeo'] or 'N/D'})")
    print(f"  CIIU             : {empresa['ciiu'] or 'N/D'}")
    print(f"  Situación        : [{empresa['situacion_empresa_codigo']}] {empresa['situacion_empresa_descripcion']}")
    print(f"  Estado Encuesta  : {empresa['estado_encuesta']} | Estado Crítica: {empresa['estado_critica']}")
    print("-" * 80)
    print("\033[1;34mCONTACTO PRINCIPAL:\033[0m")
    print(f"  Nombre           : {empresa['contacto_principal_nombre']}")
    print(f"  Cargo            : {empresa['contacto_principal_cargo']}")
    print(f"  Teléfono/Celular : {empresa['contacto_principal_telefono'] or 'No registrado'}")
    print(f"  Correo           : {empresa['contacto_principal_correo'] or 'No registrado'}")
    if empresa['wa_link']:
        print(f"  Enlace WhatsApp  : \033[4;92m{empresa['wa_link']}\033[0m")
    print("-" * 80)
    if empresa['contacto_alternativo_nombre'] or empresa['contacto_alternativo_telefono']:
        print("\033[1;33mCONTACTO ALTERNATIVO (Planilla / EDO histórico):\033[0m")
        print(f"  Nombre           : {empresa['contacto_alternativo_nombre'] or '-'}")
        print(f"  Cargo            : {empresa['contacto_alternativo_cargo'] or '-'}")
        print(f"  Teléfono         : {empresa['contacto_alternativo_telefono'] or '-'}")
        print(f"  Correo           : {empresa['contacto_alternativo_correo'] or '-'}")
        print("-" * 80)

def loop_interactivo():
    df = cargar_datos()
    
    # Configuración de pandas para visualización
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    pd.set_option("display.max_colwidth", 40)

    print("\n" + "=" * 70)
    print("  \033[1;36mTERMINAL DE CONSULTA DE EMPRESAS — EDO 2026 (PANDAS CLI)\033[0m")
    print(f"  Total empresas cargadas: \033[1m{len(df)}\033[0m")
    print("=" * 70)
    print("Comandos disponibles:")
    print("  - Escribe cualquier texto o RUC para buscar.")
    print("  - \033[1mregion <nombre>\033[0m : Filtrar por región (ej: region ancash)")
    print("  - \033[1msit <numero>\033[0m    : Filtrar por código de situación (ej: sit 0 o sit 9)")
    print("  - \033[1mwa\033[0m              : Ver solo empresas que tienen WhatsApp habilitado")
    print("  - \033[1mpy\033[0m              : Abrir terminal interactiva de Python con la variable `df`")
    print("  - \033[1msalir\033[0m o \033[1mq\033[0m        : Salir de la consola")
    print("-" * 70)

    while True:
        try:
            query = input("\033[1;32medo-cli>\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo...")
            break

        if not query:
            continue

        q_lower = query.lower()
        if q_lower in ("salir", "q", "exit"):
            print("Cerrando terminal de consulta. ¡Buen trabajo!")
            break

        if q_lower == "py":
            print("\n\033[93m[Consola Python activa. El DataFrame de empresas está en la variable `df`.]\033[0m")
            print("Ejemplos útiles:")
            print("  >>> df[df['region'] == 'Áncash'][['ruc', 'razon_social']]")
            print("  >>> df['situacion_empresa_descripcion'].value_counts()")
            print("Escribe exit() para volver a la búsqueda rápida.\n")
            import code
            code.interact(local={"df": df, "pd": pd})
            continue

        if q_lower == "wa":
            sub = df[df["wa_link"] != ""]
            formatear_tabla(sub)
            continue

        if q_lower.startswith("region "):
            reg_filtro = quitar_acentos(query[7:].strip())
            sub = df[df["region"].apply(quitar_acentos).str.contains(reg_filtro, na=False)]
            formatear_tabla(sub)
            continue

        if q_lower.startswith("sit "):
            sit_cod = query[4:].strip()
            if sit_cod.isdigit():
                sub = df[df["situacion_empresa_codigo"] == int(sit_cod)]
                formatear_tabla(sub)
            continue

        # Si es un RUC exacto de 11 dígitos
        if re.match(r"^\d{11}$", query):
            match = df[df["ruc"] == query]
            if not match.empty:
                mostrar_detalle(match.iloc[0])
                continue

        # Búsqueda general por texto / RUC parcial
        patron = quitar_acentos(query)
        res = df[df["_busqueda"].str.contains(patron, na=False, regex=False)]
        
        if len(res) == 1:
            mostrar_detalle(res.iloc[0])
        else:
            formatear_tabla(res)

if __name__ == "__main__":
    loop_interactivo()
