# Proyecto de Minería de Datos - Semana 7

## Reglas de Integración y Flujo de Trabajo

Con el propósito de garantizar la integridad del código y mantener el control de versiones del proyecto, el equipo de desarrollo debe acogerse de manera estricta al siguiente flujo de trabajo:

1. **Sincronización del entorno local:** Antes de iniciar cualquier tarea, es obligatorio actualizar el repositorio local ejecutando `git checkout main` seguido de `git pull`.

**Desarrollo aislado (Feature Branches):** Cada integrante debe trabajar exclusivamente en la rama asignada a su dimensión de análisis:
   - Integrante 1: `feature/dimension-poblacional`
   - Oscar_Robayo_Rol_1: `feature/dimension-poblacional`
   - Carlos_Pinilla_rol_2: `feature/dimension-territorial`
   - Miguel_Munar_rol_3_4: `feature/dimension-temporal`, `feature/dimension-multivariada`.

3. **Trazabilidad:** Los cambios deben confirmarse en la rama correspondiente. Se exige un mínimo de tres (3) commits con descripciones técnicas claras sobre el desarrollo realizado.

4. **Carga al repositorio remoto:** Una vez consolidado el avance, la rama local debe sincronizarse con GitHub ejecutando `git push`.

5. **Solicitud de integración (Pull Request):** Se debe crear un Pull Request (PR) en la plataforma apuntando hacia la rama base `main`.

6. **Revisión de código (Code Review):** Es indispensable solicitar la revisión técnica por parte del Integrante 1 (Administrador del repositorio). Las observaciones o correcciones reportadas deberán ser subsanadas para proceder.

7. **Fusión (Merge):** Únicamente el Administrador del repositorio tiene los permisos y la autorización para aprobar y fusionar los Pull Requests. Queda estrictamente prohibido realizar commits directos sobre la rama `main`.