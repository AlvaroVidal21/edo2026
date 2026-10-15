#!/usr/bin/env python3
"""
scripts/cargar_excel_a_bitacora.py
---------------------------------
Script para limpiar, normalizar e insertar la carga de empresas (AlvaVidalCarga.xlsx)
en la base de datos de la Bitácora EDO 2026.

Reglas aplicadas:
- RN-001 / RN-002: RUC único y válido de 11 dígitos.
- RN-003: Mantiene estados independientes (Encuesta, Crítica, Contacto).
- RN-004 / RN-005: Contacto principal obligatorio y alternativo opcional.
- RN-039: Mapeo de Situación de Empresa (código institucional 0 a 11).
- RN-042: Normalización de números telefónicos y enlace de WhatsApp (+51).
- Soporte dual: Genera SQL / Inserta directo en PostgreSQL / Exporta a CSV limpio.
"""

import sys
import re
import argparse
import unicodedata
from pathlib import Path
import pandas as pd
import openpyxl

# Mapeo de códigos de situación institucional según RN-039 y 01_modelo_negocio.md
MAPA_SITUACIONES = {
    0: "Sin clasificar / En proceso inicial",
    1: "Completado",
    2: "Fusionada/Absorbida",
    3: "Paralizada",
    4: "Liquidada",
    5: "De baja",
    6: "Suspensión temporal",
    7: "Empresas del Estado",
    8: "No ingresó al aplicativo a gestionar la encuesta",
    9: "Se negó a dar información (rechazo)",
    10: "No ubicada",
    11: "En proceso: quedó pendiente de terminar; pese a la insistencia, nunca terminó."
}

def limpiar_texto(valor):
    """Limpia cadenas, elimina espacios sobrantes y valores centinela como '0', '-', 'nan'."""
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if texto in ("0", "-", "nan", "None", "NULL"):
        return ""
    return re.sub(r"\s+", " ", texto)

def normalizar_telefono(tel_raw):
    """
    Extrae dígitos y limpia teléfonos peruanos.
    Retorna (telefono_formateado, link_whatsapp).
    """
    if not tel_raw:
        return "", ""
    
    # Extraer dígitos
    digitos = re.sub(r"\D", "", str(tel_raw))
    if not digitos or digitos in ("0", "00"):
        return "", ""
    
    # Si viene con 043... u otro código de ciudad prefijado con 0
    if len(digitos) > 9 and digitos.startswith("51"):
        numero_completo = digitos
        numero_local = digitos[2:]
    elif len(digitos) == 9 and digitos.startswith("9"):
        numero_completo = f"51{digitos}"
        numero_local = digitos
    elif len(digitos) == 8 and digitos.startswith("0"): # ej 043429631 -> 43429631
        numero_completo = f"51{digitos[1:]}"
        numero_local = digitos[1:]
    else:
        numero_local = digitos
        numero_completo = f"51{digitos}" if len(digitos) == 9 else ""

    # Generar link de WhatsApp solo si es celular móvil de 9 dígitos (9XX XXX XXX)
    wa_link = f"https://wa.me/{numero_completo}" if (len(numero_completo) == 11 and numero_completo.startswith("519")) else ""
    return numero_local, wa_link

def procesar_excel(ruta_excel: Path) -> pd.DataFrame:
    """Lee el Excel a partir de la fila 4 usando las coordenadas exactas de columnas."""
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb.active
    
    registros = []
    # min_row=4 porque filas 1 y 2 son encabezados de sección, fila 3 son nombres de columnas
    for row in ws.iter_rows(min_row=4, values_only=True):
        if not any(row):
            continue

        # row es una tupla 0-indexada correspondiente a A=0, B=1, ...
        # F=5 (RUC), G=6 (RAZÓN SOCIAL), E=4 (Región), H=7 (codciiu_2025), I=8 (ubigeo)
        ruc_raw = row[5] if len(row) > 5 else None
        ruc = re.sub(r"\D", "", str(ruc_raw or "").split(".")[0])
        if not re.match(r"^\d{11}$", ruc):
            continue

        razon_social = limpiar_texto(row[6])
        region = limpiar_texto(row[4])
        ciiu = limpiar_texto(row[7]) or (limpiar_texto(row[25]) if len(row) > 25 else "")
        ubigeo = limpiar_texto(row[8]) or (limpiar_texto(row[24]) if len(row) > 24 else "")

        # Contacto Principal: N=13 (Nombres), O=14 (Cargo), P=15 (Fijo), Q=16 (Celular), R=17 (Correo)
        contacto_nombre = limpiar_texto(row[13])
        contacto_cargo = limpiar_texto(row[14])
        
        # Teléfono principal (Q, P, U=20, BD=55)
        tel_cel = limpiar_texto(row[16])
        tel_fijo = limpiar_texto(row[15])
        tel_emp = limpiar_texto(row[20]) if len(row) > 20 else ""
        tel_sunafil = limpiar_texto(row[55]) if len(row) > 55 else ""
        tel_principal_raw = tel_cel or tel_fijo or tel_emp or tel_sunafil
        tel_principal, wa_link = normalizar_telefono(tel_principal_raw)

        # Correo principal: R=17, K=10, J=9, T=19
        correo_principal = (limpiar_texto(row[17]) or 
                            limpiar_texto(row[10]) or 
                            limpiar_texto(row[9]) or 
                            (limpiar_texto(row[19]) if len(row) > 19 else ""))

        # Contacto Alternativo (EDO 2025: AE=30, AF=31, AG=32, AH=33; AK=36, AL=37, AM=38, AN=39)
        alt_nombre = (limpiar_texto(row[30]) if len(row) > 30 else "") or (limpiar_texto(row[36]) if len(row) > 36 else "")
        alt_cargo = (limpiar_texto(row[31]) if len(row) > 31 else "") or (limpiar_texto(row[37]) if len(row) > 37 else "")
        alt_tel_raw = (limpiar_texto(row[33]) if len(row) > 33 else "") or (limpiar_texto(row[39]) if len(row) > 39 else "") or (limpiar_texto(row[28]) if len(row) > 28 else "")
        alt_tel, _ = normalizar_telefono(alt_tel_raw)
        alt_correo = (limpiar_texto(row[32]) if len(row) > 32 else "") or (limpiar_texto(row[38]) if len(row) > 38 else "")

        # Si el alternativo es idéntico al principal, no duplicar
        if alt_nombre.lower() == contacto_nombre.lower():
            alt_nombre, alt_cargo, alt_tel, alt_correo = "", "", "", ""

        # Situación institucional: W=22, Observación: X=23
        sit_code_raw = str(row[22]).split(".")[0].strip() if len(row) > 22 and row[22] is not None else "0"
        sit_code = int(sit_code_raw) if sit_code_raw.isdigit() else 0

        obs = str(row[23]).strip() if len(row) > 23 and row[23] is not None else ""
        estado_contacto = "contactado" if obs == "ACTUALIZADO" else "pendiente"
        estado_encuesta = "por_contactar"
        estado_critica = "sin_iniciar"

        registros.append({
            "ruc": ruc,
            "razon_social": razon_social,
            "region": region,
            "ciiu": ciiu,
            "ubigeo": ubigeo,
            "contacto_principal_nombre": contacto_nombre if contacto_nombre else "POR IDENTIFICAR",
            "contacto_principal_cargo": contacto_cargo if contacto_cargo else "No especificado",
            "contacto_principal_telefono": tel_principal,
            "contacto_principal_correo": correo_principal,
            "wa_link": wa_link,
            "contacto_alternativo_nombre": alt_nombre,
            "contacto_alternativo_cargo": alt_cargo,
            "contacto_alternativo_telefono": alt_tel,
            "contacto_alternativo_correo": alt_correo,
            "situacion_empresa_codigo": sit_code,
            "situacion_empresa_descripcion": MAPA_SITUACIONES.get(sit_code, "Otro"),
            "estado_contacto": estado_contacto,
            "correo_confirmado": False,
            "estado_encuesta": estado_encuesta,
            "estado_critica": estado_critica
        })

    print(f"[OK] Procesadas {len(registros)} filas desde '{ruta_excel.name}'.")
    df_limpio = pd.DataFrame(registros)
    df_limpio = df_limpio.drop_duplicates(subset=["ruc"], keep="first")
    return df_limpio

def generar_sql_insert(df: pd.DataFrame, ruta_sql: Path):
    """Genera script SQL compatible con PostgreSQL / SQLite."""
    with open(ruta_sql, "w", encoding="utf-8") as f:
        f.write("-- Script de carga inicial generado automáticamente\n")
        f.write("-- Bitácora Laboral y Sustento de Crítica EDO 2026\n\n")
        
        for _, row in df.iterrows():
            def esc(txt):
                return str(txt or "").replace("'", "''")

            f.write(
                "INSERT INTO empresa ("
                "ruc, razon_social, region, ciiu, "
                "contacto_principal_nombre, contacto_principal_cargo, "
                "contacto_principal_telefono, contacto_principal_correo, "
                "contacto_alternativo_nombre, contacto_alternativo_cargo, "
                "contacto_alternativo_telefono, contacto_alternativo_correo, "
                "situacion_empresa, estado_contacto, correo_confirmado, "
                "estado_encuesta, estado_critica"
                ") VALUES ("
                f"'{esc(row['ruc'])}', '{esc(row['razon_social'])}', '{esc(row['region'])}', '{esc(row['ciiu'])}', "
                f"'{esc(row['contacto_principal_nombre'])}', '{esc(row['contacto_principal_cargo'])}', "
                f"'{esc(row['contacto_principal_telefono'])}', '{esc(row['contacto_principal_correo'])}', "
                f"'{esc(row['contacto_alternativo_nombre'])}', '{esc(row['contacto_alternativo_cargo'])}', "
                f"'{esc(row['contacto_alternativo_telefono'])}', '{esc(row['contacto_alternativo_correo'])}', "
                f"{row['situacion_empresa_codigo']}, '{esc(row['estado_contacto'])}', {row['correo_confirmado']}, "
                f"'{esc(row['estado_encuesta'])}', '{esc(row['estado_critica'])}'"
                ") ON CONFLICT (ruc) DO UPDATE SET "
                "situacion_empresa = EXCLUDED.situacion_empresa, "
                "contacto_principal_telefono = EXCLUDED.contacto_principal_telefono, "
                "contacto_principal_correo = EXCLUDED.contacto_principal_correo;\n"
            )
    print(f"[OK] Archivo SQL generado en: {ruta_sql}")

def main():
    parser = argparse.ArgumentParser(description="Procesar e importar carga EDO 2026 a la Bitácora.")
    parser.add_argument("--excel", default="AlvaVidalCarga.xlsx", help="Ruta al archivo Excel")
    parser.add_argument("--csv", default="carga_limpia_edo2026.csv", help="Ruta de salida CSV limpio")
    parser.add_argument("--sql", default="carga_inicial_empresas.sql", help="Ruta de salida SQL")
    parser.add_argument("--pg-conn", help="Cadena de conexión PostgreSQL (ej: postgresql://user:pass@localhost:5432/bitacora_edo)")

    args = parser.parse_args()
    excel_path = Path(args.excel)
    
    if not excel_path.exists():
        print(f"[ERROR] No se encontró el archivo '{excel_path}'.")
        sys.exit(1)

    print(f"[*] Iniciando limpieza y adecuación de '{excel_path}'...")
    df_limpio = procesar_excel(excel_path)
    
    # Exportar CSV
    csv_path = Path(args.csv)
    df_limpio.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Exportado CSV limpio: {csv_path} ({len(df_limpio)} empresas)")

    # Exportar SQL
    sql_path = Path(args.sql)
    generar_sql_insert(df_limpio, sql_path)

    # Inserción opcional directa en PostgreSQL
    if args.pg_conn:
        try:
            import psycopg
            print(f"[*] Conectando a PostgreSQL en '{args.pg_conn}'...")
            with psycopg.connect(args.pg_conn) as conn:
                with conn.cursor() as cur:
                    with open(sql_path, "r", encoding="utf-8") as f:
                        cur.execute(f.read())
                conn.commit()
            print("[OK] Datos insertados exitosamente en la base de datos PostgreSQL.")
        except Exception as e:
            print(f"[ERROR] No se pudo insertar directamente en PostgreSQL: {e}")

    # Resumen de calidad
    con_cel = len(df_limpio[df_limpio["contacto_principal_telefono"] != ""])
    con_wa = len(df_limpio[df_limpio["wa_link"] != ""])
    con_correo = len(df_limpio[df_limpio["contacto_principal_correo"] != ""])
    print("\n" + "="*50)
    print("RESUMEN DE CALIDAD DE LA CARGA:")
    print(f"- Total de empresas procesadas: {len(df_limpio)}")
    print(f"- Con teléfono principal asignado: {con_cel} / {len(df_limpio)}")
    print(f"- Con enlace directo a WhatsApp: {con_wa} / {len(df_limpio)}")
    print(f"- Con correo electrónico asignado: {con_correo} / {len(df_limpio)}")
    print("="*50)

if __name__ == "__main__":
    main()
