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


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")


def recomendar(
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

    faltantes = []
    if not objetivo:
        faltantes.append("¿Cuál es tu objetivo principal?")
    if tiempo is None or tiempo <= 0:
        faltantes.append("¿Cuántos minutos tienes disponibles?")
    if faltantes:
        return "## Necesito aclarar esto\n\n" + "\n\n".join(faltantes[:2])

    candidatos = [r for r in RUTINAS if r["objetivo"] == objetivo and r["nivel"] == nivel]
    compatibles = [r for r in candidatos if equipo in r["equipos"] and r["duracion"] <= tiempo]
    if not compatibles:
        compatibles = [r for r in RUTINAS if r["objetivo"] == objetivo and r["duracion"] <= tiempo]
    if not compatibles:
        compatibles = sorted(RUTINAS, key=lambda r: abs(r["duracion"] - tiempo))

    rutina = min(
        compatibles,
        key=lambda r: (r["intensidad"] != intensidad, abs(r["duracion"] - tiempo)),
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
Coincide con tu objetivo de **{objetivo.lower()}**, nivel **{nivel.lower()}**, tiempo disponible y equipo seleccionado.

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
        gr.Dropdown(["Mejorar fuerza", "Mejorar resistencia", "Movilidad", "Bienestar general"], label="Objetivo"),
        gr.Radio(["Principiante", "Intermedio"], value="Principiante", label="Nivel"),
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
        ["Mejorar fuerza", "Principiante", 30, "Sin equipo", "Media", "Ninguna", ""],
        ["Movilidad", "Principiante", 20, "Sin equipo", "Baja", "Ligera", "Trabajo muchas horas sentado."],
        ["Mejorar resistencia", "Intermedio", 35, "Sin equipo", "Alta", "Moderada", "Tengo dolor de rodilla."],
    ],
    flagging_mode="never",
)


if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
