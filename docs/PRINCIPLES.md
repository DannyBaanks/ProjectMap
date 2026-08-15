# PRINCIPLES — ProjectMap

## 1. Zero invasión
- `scan` es read-only: no mueve, renombra, borra ni modifica archivos del repo.
- No instala nada dentro del proyecto analizado.
- El repo no depende de ProjectMap; no necesita una marca de ProjectMap; no
  necesita que aparezca nombre del autor. Literalmente puede ser:

      repo/ -> ProjectMap -> resultado

  y el repo queda exactamente igual.

## 2. Sin branding por defecto
Dos modos de export:
- `projectmap export github` → **neutral**: language map, architecture metadata,
  GitHub-compatible output. Sin "Powered by Danny", sin "Made by ISyCo", sin
  "ProjectMap™".
- `projectmap export github --branding` → opcional, si alguien quiere mostrarlo.

El objetivo no es que vean ProjectMap; es que vean correctamente el proyecto.
Infraestructura invisible. Si alguien lo usa y nadie sabe que lo usó, ganamos.

## 3. Todo local (MVP)
```
repo -> scanner local -> model local -> output local
```
No se envía el código a ningún servidor. Cloud futuro sería opt-in y explícito.
Así evitamos el problema de "¿a dónde se fue mi código?".

## 4. Evidence before narrative
El sistema distingue:
- VERIFIED   — observado directamente con alta certeza
- INFERRED   — heurística razonable pero no definitiva
- DECLARED   — declarado por el autor via manifest
- UNKNOWN    — no se pudo determinar
- CONFLICTING— evidencias contradictorias

Nunca presentar una inferencia como hecho.

## 5. No sobreingeniería
Sin microservicios, DB, cloud, auth, GitHub App, web dashboard, LLM dependency,
distributed graph. Queremos: repo -> scan -> model -> output. Si eso funciona,
escalamos.

## 6. MEOW es un fixture, no una dependencia
MEOW-ENGINE es el "motivating example" y caso cabrón de prueba. El core NO lo
importa, no conoce sus reglas, no tiene nada de MEOW dentro. Si ProjectMap
puede modelar MEOW sin tocar el core, la abstracción sirvió.

## 7. Diff safety
ProjectMap nunca: borra archivos del usuario, reescribe README sin permiso,
modifica código, toca git history, ejecuta git reset, hace force push.
Comandos que modifican el repo son explícitos (`init`, `export --target ...`).
Por defecto: `scan` = read-only.
