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

La entrada incluye estatura, peso, IMC estimado, objetivo, nivel (principiante,
intermedio o avanzado), tiempo, equipo, intensidad y actividad reciente. El IMC
es únicamente informativo y no se utiliza de forma aislada para prescribir una rutina.

Si no existe una coincidencia total en el catálogo, la aplicación identifica la
opción como alternativa cercana y declara los criterios que no coinciden. Las
solicitudes de dieta, nutrición, suplementación o medicación se consideran fuera
del alcance y se derivan a un profesional calificado.

## Privacidad y limitaciones

- La demo no requiere nombre, correo, historia clínica ni credenciales.
- Para pruebas académicas se utilizan datos ficticios o anonimizados.
- No deben ingresarse datos sensibles o información real de terceros.
- IronCoach no diagnostica, trata, prescribe rehabilitación ni sustituye a un
  profesional de salud, nutrición o entrenamiento.
- El catálogo es ficticio y limitado; las recomendaciones son orientación general.

## Demostración pública

- Aplicación: https://milenaguirre-ironcoach.hf.space
- Código fuente: https://github.com/MilenkoAguirre/IronCoach
- Prompt y reglas: [PROMPT_IRONCOACH.md](PROMPT_IRONCOACH.md)

## Ejecución local

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:7860` en el navegador.

## Hugging Face Spaces

Crea un Space con SDK Gradio y copia el contenido de esta carpeta en la raíz del
repositorio del Space. No se requieren claves ni variables secretas.
