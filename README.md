# Proyecto de Minería de Datos - Semana 7

## Reglas de Integración y Flujo de Trabajo

Con el propósito de mantener la integridad y el orden en el repositorio, todos los integrantes del equipo de desarrollo deberán acogerse estrictamente al siguiente flujo de trabajo para la integración de código:

1. **Actualización del entorno local:** Antes de iniciar cualquier desarrollo, es imperativo actualizar la versión local ejecutando `git checkout main` seguido de `git pull`.

2. **Uso de ramas asignadas:** Cada desarrollador deberá trabajar exclusivamente en la rama correspondiente a su dimensión de análisis:
   - Oscar_Robayo_Rol_1: `feature/dimension-poblacional`
   - Carlos_Pinilla_rol_2: `feature/dimension-territorial`
   - Miguel_Munar_rol_3_4: `feature/dimension-temporal`, `feature/dimension-multivariada`.

3. **Desarrollo y Commits:** Los cambios deben realizarse dentro de la rama asignada. Se requiere un mínimo de tres (3) commits con descripciones técnicas y claras relacionadas con la dimensión analizada.

4. **Carga de cambios (Push):** Una vez finalizado el desarrollo, la rama local debe sincronizarse con el repositorio remoto mediante el comando `git push`.

5. **Pull Request (PR):** Se debe generar un *Pull Request* desde la plataforma de GitHub apuntando hacia la rama `main`.

6. **Revisión de Código:** Es necesario solicitar la revisión técnica por parte del Integrante 1 (Administrador del repositorio). En caso de existir observaciones, estas deberán ser subsanadas antes de su aprobación.

7. **Fusión (Merge):** Únicamente el Integrante 1 posee los permisos para aprobar y fusionar los *Pull Requests* hacia la rama `main`. Queda estrictamente prohibido realizar *commits* directos sobre la rama principal.