"""Lectura por bloques de la carga EDO, sin confundir encabezados repetidos."""

import re
import unicodedata

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

MISSING = {"", "0", "-", "s/n", "sin dato", "no tiene", "nan", "none"}
CONTACT_BLOCKS = [
    ("Datos actualizados", "N", "O", "R", "Q", "P", None, "S"),
    ("EDO 2025 · informante 1", "AE", "AF", "AG", "AH", "AJ", "AI", None),
    ("EDO 2025 · informante 2", "AK", "AL", "AM", "AN", "AP", "AO", None),
    ("EDO 2024 · informante 1", "AQ", "AR", "AS", "AT", "AV", "AU", None),
    ("EDO 2024 · informante 2", "AW", "AX", "AY", "AZ", "BB", "BA", None),
]


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return "" if text.casefold() in MISSING else text


def person_key(name):
    name = unicodedata.normalize("NFKD", name.casefold())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in name if not unicodedata.combining(c)))


def emails(value):
    result = []
    raw = clean_text(value)
    for part in re.split(r"[,;/|\n]+", raw):
        candidates = [part.strip().removeprefix("mailto:")]
        candidates += re.findall(r"[^\s<>:;,/|]+@[^\s<>:;,/|]+", part)
        for candidate in candidates:
            candidate = candidate.strip(" <>\"'")
            try:
                validate_email(candidate)
            except ValidationError:
                continue
            # El dominio no distingue mayúsculas; se conserva el texto local.
            local, domain = candidate.rsplit("@", 1)
            candidate = f"{local}@{domain.lower()}"
            if candidate.casefold() not in {item.casefold() for item in result}:
                result.append(candidate)
    return result


def phones(value, city_code=""):
    result = []
    if not clean_text(value):
        return result
    raw = str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)
    parts = re.split(
        r"[,;/|\n]+|\s+[yY]\s+|(?<=\d)\s*-\s*(?=\+?\d{6,})|(?<=\d)\.(?=\()",
        raw,
    )
    for part in parts:
        # Un anexo no forma parte del número al que se llama.
        part = re.split(r"\b(?:anexo|anx|ext)\b\.?", part, flags=re.IGNORECASE)[0]
        digits = re.sub(r"\D", "", part)
        if digits.startswith("0051"):
            digits = digits[2:]
        if not 6 <= len(digits) <= 11:
            continue
        code = re.sub(r"\D", "", clean_text(city_code)).lstrip("0")
        if len(digits) in {6, 7} and 1 <= len(code) <= 2:
            digits = code + digits
        if digits not in result:
            result.append(digits)
    return result


def whatsapp_url(value):
    for phone in phones(value):
        if re.fullmatch(r"9\d{8}", phone):
            return f"https://wa.me/51{phone}"
        if re.fullmatch(r"519\d{8}", phone):
            return f"https://wa.me/{phone}"
    return ""


def sourced_values(row, columns, parser, source, city_code=""):
    values = []
    seen = set()
    for column in columns:
        if not column:
            continue
        parsed = parser(row.get(column), city_code) if parser is phones else parser(row.get(column))
        for value in parsed:
            if value.casefold() not in seen:
                values.append({"valor": value, "fuente": source, "columna": column})
                seen.add(value.casefold())
    return values


def prepare_company(row):
    contacts = []
    for source, name, role, email, mobile, landline, city, extra_email in CONTACT_BLOCKS:
        contact = {
            "fuente": source,
            "nombre": clean_text(row.get(name)),
            "cargo": clean_text(row.get(role)),
            "columna_nombre": name,
            "columna_cargo": role,
            "correos": sourced_values(row, [email, extra_email], emails, source),
            "telefonos": sourced_values(row, [mobile, landline], phones, source, row.get(city)),
        }
        if any(contact[key] for key in ("nombre", "cargo", "correos", "telefonos")):
            contacts.append(contact)

    generic_emails = []
    for columns, source in [
        (["K", "M"], "Envío EDO 2026 · correo prioritario"),
        (["J", "L"], "Directorio base · correo sistema"),
        (["T"], "Datos actualizados · empresa"),
        (["AD"], "Planilla electrónica 2025 · empresa"),
        (["BC"], "SUNAFIL"),
    ]:
        generic_emails += sourced_values(row, columns, emails, source)
    generic_phones = sourced_values(row, ["U"], phones, "Datos actualizados · empresa")
    generic_phones += sourced_values(row, ["AC"], phones, "Planilla electrónica 2025 · empresa", row.get("AB"))
    generic_phones += sourced_values(row, ["BD"], phones, "SUNAFIL")

    # Nombre y cargo se toman de la misma persona. No se mezclan informantes distintos.
    primary = next((contact for contact in contacts if contact["nombre"]), contacts[0] if contacts else None)
    primary_key = person_key(primary["nombre"]) if primary else ""
    alternate = next(
        (contact for contact in contacts if contact["nombre"] and person_key(contact["nombre"]) != primary_key),
        None,
    )
    values = {
        "razon_social": clean_text(row.get("G")),
        "region": clean_text(row.get("E")) or "Sin dato",
        "ciiu": clean_text(row.get("Z")) or clean_text(row.get("H")) or "Sin dato",
    }
    origins = {
        "ciiu": "Planilla electrónica 2025 · Z" if clean_text(row.get("Z")) else "Directorio base · H",
    }
    for prefix, selected in [("contacto_principal", primary), ("contacto_alternativo", alternate)]:
        same_person = []
        if selected:
            same_person = [selected] + [
                contact for contact in contacts
                if contact is not selected and selected["nombre"] and person_key(contact["nombre"]) == person_key(selected["nombre"])
            ]
        for field, key in [("nombre", "columna_nombre"), ("cargo", "columna_cargo")]:
            donor = next((contact for contact in same_person if contact[field]), None)
            values[f"{prefix}_{field}"] = donor[field] if donor else ""
            if donor:
                origins[f"{prefix}_{field}"] = f"{donor['fuente']} · {donor[key]}"
        for field, key, fallback in [("correo", "correos", generic_emails), ("telefono", "telefonos", generic_phones)]:
            candidates = [item for contact in same_person for item in contact[key]]
            if prefix == "contacto_principal":
                # Si el contacto actualizado no tiene nombre, sus canales siguen disponibles.
                candidates += [item for contact in contacts if not contact["nombre"] and contact is not selected for item in contact[key]]
                candidates += fallback
            chosen = candidates[0] if candidates else None
            values[f"{prefix}_{field}"] = chosen["valor"] if chosen else ""
            if chosen:
                origins[f"{prefix}_{field}"] = f"{chosen['fuente']} · {chosen['columna']}"

    all_emails = [item for contact in contacts for item in contact["correos"]] + generic_emails
    all_phones = [item for contact in contacts for item in contact["telefonos"]] + generic_phones
    metadata = {
        "contactos": contacts,
        "correos": all_emails,
        "telefonos": all_phones,
        "origenes": origins,
        "valores_importados": values.copy(),
        "columnas": {key: "" if value is None else str(value) for key, value in row.items()},
    }
    return values, metadata
