---
title: IronCoach
emoji: 🏋️
colorFrom: red
colorTo: gray
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
---

# IronCoach

Prototipo académico de IronTrack que recomienda rutinas generales mediante reglas
transparentes y un catálogo ficticio. No diagnostica, trata ni sustituye a un
profesional de salud o entrenamiento.

## Ejecución local

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:7860` en el navegador.

## Hugging Face Spaces

Crea un Space con SDK Gradio y copia el contenido de esta carpeta en la raíz del
repositorio del Space. No se requieren claves ni variables secretas.
