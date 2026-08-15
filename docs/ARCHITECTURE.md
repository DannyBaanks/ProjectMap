# ARCHITECTURE — ProjectMap

## Principio
**ProjectMap is not an architecture for your project. It is a model of your project.**

No llega dictando "tu proyecto debe tener Core/Registry/Adapters". Llega diciendo:
"esto es lo que pude observar; aquí está la evidencia; esto es inferido; esto fue
declarado por el autor."

## Flujo
```
REPO DEL USUARIO
      |  read-only
      v
 PROJECTMAP
      |
      +---> Project Model  ---> Exporters (JSON/Markdown/GitHub artefacts)
      |
      +---> NO modifica código, NO renombra, NO instala nada en el repo,
            NO requiere que el repo dependa de ProjectMap, NO deja marca.
```

`projectmap scan repo/` es **read-only**. El repo queda exactamente igual.

## Capas
```
core/        project model, contracts, evidence — NO conoce GitHub ni MEOW
scanners/    recorre el repo (read-only) y recolecta signals
detectors/   language / role / component detection (heurísticas + manifest)
graph/       relations entre componentes
exporters/   json / markdown / github artefacts
cli/         comandos scan/init/inspect/export/validate
adapters/    github (futuro), local — el core no los importa
```

## Dependencia
La dependencia SIEMPRE apunta hacia afuera:
```
ProjectMap Core -> Project Model -> Adapters -> Platforms
```
NUNCA al revés. El core no importa un SDK de GitHub ni código de MEOW.

## Plataforma
El core funciona sin GitHub. El adapter de GitHub (futuro) produce artefactos
locales (`.gitattributes`, reportes, badges) sólo cuando el usuario lo pide
explícitamente con `projectmap export --target github`. No hace push solo.

## Privacidad
Todo es local en el MVP. No se envía el código a ningún servidor.
"Lee → interpreta → genera → se va."
