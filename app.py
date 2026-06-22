"""Prototipo funcional de IronCoach para IronTrack."""

from __future__ import annotations

import json
import os
import unicodedata
from pathlib import Path

import gradio as gr


BASE_DIR = Path(__file__).resolve().parent
with (BASE_DIR / "catalogo_rutinas.json").open(encoding="utf-8") as archivo:
    RUTINAS = json.load(archivo)

PALABRAS_RIESGO = (
    "dolor",
    "lesion",
    "lesionado",
    "mareo",
    "embarazo",
    "embarazada",
    "condicion medica",
    "rehabilitacion",
    "operacion",
    "cirugia",
)

PALABRAS_FUERA_ALCANCE = (
    "dieta",
    "nutricion",
    "suplemento",
    "suplementacion",
    "medicamento",
)


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")


def recomendar(
    estatura_cm: int | float | None,
    peso_kg: int | float | None,
    objetivo: str,
    nivel: str,
    tiempo: int | float | None,
    equipo: str,
    intensidad: str,
    actividad_reciente: str,
    observaciones: str,
) -> str:
    """Selecciona una rutina mediante reglas visibles y aplica controles de seguridad."""
    observaciones_limpias = normalizar(observaciones or "")
    riesgos = [palabra for palabra in PALABRAS_RIESGO if palabra in observaciones_limpias]
    if riesgos:
        return (
            "## Recomendación detenida\n\n"
            "Mencionaste una situación que requiere evaluación individual. IronCoach no "
            "diagnostica ni prescribe rehabilitación. Consulta a un profesional de salud "
            "o entrenamiento calificado antes de iniciar o modificar una rutina. Si los "
            "síntomas son intensos o repentinos, busca atención médica."
        )

    solicitudes_fuera_alcance = [
        palabra for palabra in PALABRAS_FUERA_ALCANCE if palabra in observaciones_limpias
    ]
    if solicitudes_fuera_alcance:
        return (
            "## Solicitud fuera de alcance\n\n"
            "IronCoach se limita a orientar sobre rutinas generales del catálogo de "
            "IronTrack. No ofrece planes de nutrición, dietas, suplementación ni "
            "medicación. Consulta a un profesional calificado para recibir orientación "
            "individual sobre esos temas."
        )

    faltantes = []
    if estatura_cm is None or not 100 <= estatura_cm <= 230:
        faltantes.append("¿Cuál es tu estatura válida en centímetros (100–230 cm)?")
    if peso_kg is None or not 30 <= peso_kg <= 300:
        faltantes.append("¿Cuál es tu peso válido en kilogramos (30–300 kg)?")
    if not objetivo:
        faltantes.append("¿Cuál es tu objetivo principal?")
    if not nivel:
        faltantes.append("¿Cuál es tu nivel: principiante, intermedio o avanzado?")
    if tiempo is None or tiempo <= 0:
        faltantes.append("¿Cuántos minutos tienes disponibles?")
    if not equipo:
        faltantes.append("¿Qué equipo tienes disponible?")
    if not intensidad:
        faltantes.append("¿Qué intensidad deseas: baja, media o alta?")
    if faltantes:
        return "## Necesito aclarar esto\n\n" + "\n\n".join(faltantes[:2])

    imc = round(peso_kg / ((estatura_cm / 100) ** 2), 1)

    candidatos = [r for r in RUTINAS if r["objetivo"] == objetivo and r["nivel"] == nivel]
    compatibles = [r for r in candidatos if equipo in r["equipos"] and r["duracion"] <= tiempo]
    if not compatibles:
        compatibles = [
            r
            for r in RUTINAS
            if r["objetivo"] == objetivo
            and equipo in r["equipos"]
            and r["duracion"] <= tiempo
        ]
    if not compatibles:
        compatibles = [r for r in RUTINAS if r["objetivo"] == objetivo and r["duracion"] <= tiempo]
    if not compatibles:
        compatibles = list(RUTINAS)

    rutina = min(
        compatibles,
        key=lambda r: (
            equipo not in r["equipos"],
            r["intensidad"] != intensidad,
            r["nivel"] != nivel,
            abs(r["duracion"] - tiempo),
        ),
    )
    diferencias = []
    if rutina["nivel"] != nivel:
        diferencias.append(f"nivel (la rutina es {rutina['nivel'].lower()})")
    if equipo not in rutina["equipos"]:
        diferencias.append("equipo disponible")
    if rutina["intensidad"] != intensidad:
        diferencias.append(f"intensidad (la rutina es {rutina['intensidad'].lower()})")
    if rutina["duracion"] > tiempo:
        diferencias.append("tiempo disponible")

    if diferencias:
        motivo = (
            f"Es la alternativa más cercana del catálogo para tu objetivo de "
            f"**{objetivo.lower()}**. No coincide totalmente con "
            f"{', '.join(diferencias)}; revisa estas diferencias antes de iniciar."
        )
    else:
        motivo = (
            f"Coincide con tu objetivo de **{objetivo.lower()}**, nivel "
            f"**{nivel.lower()}**, tiempo disponible y equipo seleccionado."
        )
    ajuste = {
        "Ninguna": "Realiza la sesión completa y registra cómo te sentiste.",
        "Ligera": "Empieza con una ronda menos si aún notas fatiga.",
        "Moderada": "Reduce una ronda y mantén un ritmo cómodo.",
        "Intensa": "Prioriza recuperación; considera movilidad suave o descanso hoy.",
    }.get(actividad_reciente, "Ajusta el volumen según tu recuperación.")

    plan = "\n".join(f"{i}. {paso}" for i, paso in enumerate(rutina["plan"], 1))
    return f"""## Recomendación
**{rutina['nombre']}** — {rutina['duracion']} minutos, intensidad {rutina['intensidad'].lower()}.

## Motivo
{motivo}

## Datos personales considerados
- Estatura: **{estatura_cm:g} cm**
- Peso: **{peso_kg:g} kg**
- IMC estimado: **{imc} kg/m²**

El IMC se muestra como referencia general. No diagnostica el estado de salud ni determina por sí solo la rutina o la intensidad.

## Plan breve
{plan}

## Precaución
Detén la actividad si aparece dolor, mareo o malestar inusual. Esta es orientación general y no reemplaza a un profesional.

## Siguiente paso
{ajuste}
"""


demo = gr.Interface(
    fn=recomendar,
    inputs=[
        gr.Number(value=170, minimum=100, maximum=230, label="Estatura (cm)"),
        gr.Number(value=70, minimum=30, maximum=300, label="Peso (kg)"),
        gr.Dropdown(["Mejorar fuerza", "Mejorar resistencia", "Movilidad", "Bienestar general"], label="Objetivo"),
        gr.Radio(["Principiante", "Intermedio", "Avanzado"], value="Principiante", label="Nivel"),
        gr.Slider(10, 60, value=30, step=5, label="Tiempo disponible (minutos)"),
        gr.Dropdown(["Sin equipo", "Bandas", "Mancuernas"], value="Sin equipo", label="Equipo"),
        gr.Radio(["Baja", "Media", "Alta"], value="Media", label="Intensidad deseada"),
        gr.Radio(["Ninguna", "Ligera", "Moderada", "Intensa"], value="Ninguna", label="Actividad reciente"),
        gr.Textbox(lines=3, label="Observaciones", placeholder="Ej.: Prefiero ejercicios de pie."),
    ],
    outputs=gr.Markdown(label="Respuesta de IronCoach"),
    title="IronCoach — Asistente de rutinas IronTrack",
    description=(
        "Selecciona tus preferencias para recibir una orientación general basada en el "
        "catálogo ficticio de IronTrack. No ofrece diagnóstico ni tratamiento médico."
    ),
    examples=[
        [170, 70, "Mejorar fuerza", "Principiante", 30, "Sin equipo", "Media", "Ninguna", ""],
        [165, 62, "Movilidad", "Principiante", 20, "Sin equipo", "Baja", "Ligera", "Trabajo muchas horas sentado."],
        [180, 82, "Mejorar resistencia", "Avanzado", 45, "Sin equipo", "Alta", "Moderada", ""],
        [175, 75, "Mejorar resistencia", "Intermedio", 35, "Sin equipo", "Alta", "Moderada", "Tengo dolor de rodilla."],
    ],
    flagging_mode="never",
)


if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
