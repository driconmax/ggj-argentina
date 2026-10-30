# Cómo contribuir

Gracias por ayudar a construir la memoria de GGJ Argentina.

## Formas de colaborar

- Corregir errores o mejorar la redacción.
- Documentar una edición, un evento, una organización o una persona.
- Aportar guías y recursos útiles para participantes y equipos organizadores.
- Abrir un issue cuando no tengas suficiente información para proponer el cambio directamente.

## Flujo recomendado

1. Creá un fork del repositorio.
2. Trabajá en una rama con un nombre descriptivo.
3. Modificá la ficha YAML correspondiente dentro de `data/`. El contenido narrativo no estructurado permanece dentro de `docs/`.
4. Ejecutá `python hooks/site_builder.py` y luego `zensical build --strict` si tenés el entorno local instalado.
5. Abrí un pull request y explicá qué agregaste, de dónde surge la información y cómo puede verificarse.

Los cambios pequeños también pueden hacerse con el botón de edición de GitHub presente en cada página.

## Videos de una edición

Para incorporar videos en una edición, agregá una lista `videos` a su archivo en `data/editions/AAAA.yml`. Cada entrada lleva un título, el identificador de YouTube y, opcionalmente, una descripción:

```yaml
videos:
  - title: Video de las sedes argentinas
    youtube_id: jiIYst4ebic
    description: Video realizado por las sedes de Argentina.
```

El identificador es la parte que aparece después de `v=` en el enlace de YouTube. La página de la edición incorpora el video y un enlace para verlo en YouTube.

## Fichas de sede

Cada sede tiene un único archivo YAML. No edites manualmente los índices ni las páginas dentro de `docs/sedes/fichas/`: se regeneran durante la compilación.

```yaml
id: 2026-ejemplo
year: 2026
name: GGJ26 - Sede de ejemplo
province: Córdoba
locality: Ciudad de ejemplo
audience: ggj
organization_id: organizacion-ejemplo
participants: 42
participants_basis: registered_members
games: 8
organizers:
  - person_id: persona-ejemplo
source: https://ejemplo.org/fuente
```

Los campos `participants` y `games` son opcionales. Cuando se informan, deben ser enteros iguales o mayores que cero. Usá `participants_basis: registered_members` cuando la cifra provenga de los integrantes registrados en la ficha oficial de GGJ y no de un conteo de asistencia presencial. Los totales muestran tanto la suma como cuántas sedes aportaron el dato, para no presentar una cobertura parcial como total nacional.

Usá `audience: next` para una sede GGJ NEXT. Los campos `id` y `organization_id` deben ser estables. La organización referenciada debe tener una ficha en `data/organizations/`.

Cuando una misma organización tenga eventos en distintos años, sus fichas enlazan automáticamente la edición anterior y la siguiente. Si en un mismo año realizó más de un evento, todos aparecen juntos en ese paso de la cronología.

## Organizaciones

Cada organización tiene un archivo en `data/organizations/`:

```yaml
id: organizacion-ejemplo
name: Organización de ejemplo
country: AR
website: https://ejemplo.org/
summary: Breve descripción verificable.
```

El índice y la lista de participaciones se calculan a partir de los eventos que usan su `id`.

## Personas

Las personas argentinas con participación documentada tienen una ficha en `data/people/`:

```yaml
id: persona-ejemplo
name: Nombre completo
countries: [AR]
bio: Perfil breve y verificable.
photo: ../assets/images/personas/persona-ejemplo.jpg
website: https://ejemplo.org/
links:
  - label: Perfil profesional
    url: https://ejemplo.org/perfil
sources:
  - title: Fuente del perfil
    url: https://ejemplo.org/fuente
```

`bio`, `photo`, `website`, `links` y `sources` son opcionales. Las fotografías locales se guardan dentro de `docs/assets/images/personas/`; la ruta se escribe desde la página generada en `docs/personas/`.

Para reutilizar una persona en una edición o como integrante de la organización local de un evento, usá `person_id: persona-ejemplo` en lugar de repetir el nombre. Sus participaciones se agrupan automáticamente por edición. El año enlaza al resumen de esa edición y los roles de organización local enlazan a la ficha del evento.

La organización regional de un año que todavía no tenga una edición completa puede registrarse en `data/regional_organizers/AAAA.yml`. Ese dato alimenta el índice histórico y las fichas personales sin necesidad de crear estadísticas o contenidos aún desconocidos.

## Criterios editoriales

- No presentes recuerdos, cifras o fechas dudosas como hechos confirmados.
- Citá una fuente pública cuando exista; si se trata de un testimonio, indicá quién lo aportó y contá con su permiso.
- No publiques datos personales, información sensible ni fotografías sin autorización.
- Escribí en español claro y evitá asumir experiencia previa.
- Preferí cambios acotados para que sean fáciles de revisar.

## Pull requests

Al enviar un cambio confirmás que tenés derecho a compartir el material bajo las licencias indicadas en el repositorio.

Las conversaciones deben ser respetuosas y centrarse en mejorar el contenido. Los desacuerdos sobre hechos históricos deben resolverse con fuentes o señalando claramente las versiones existentes.

## Licencias y derechos de las contribuciones

Al enviar una contribución original a GGJ Argentina, aceptás que:

- **Contenido y documentación:** tu contribución se publique bajo la licencia [Creative Commons Atribución-CompartirIgual 4.0 Internacional (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
- **Código fuente:** tus contribuciones de código, scripts y configuraciones se publiquen bajo la licencia MIT.
- **Permiso especial para Global Game Jam:** otorgás a Global Game Jam, Inc. una autorización gratuita, mundial, no exclusiva e irrevocable para utilizar, reproducir, modificar, traducir y redistribuir tus contribuciones originales de contenido y documentación, incluso con fines comerciales, sin obligación de atribución ni de distribuir las adaptaciones bajo CC BY-SA 4.0.

**Conservás los derechos de autor sobre tus contribuciones.** Esta autorización no implica transferir su titularidad a GGJ Argentina ni a Global Game Jam, Inc.

Al contribuir, confirmás que sos titular de los derechos necesarios para conceder estos permisos.

Cada pull request debe incluir la confirmación expresa de estas condiciones mediante la casilla obligatoria de la plantilla. Las contribuciones anteriores a la adopción de este procedimiento no conceden retroactivamente el permiso especial a Global Game Jam, Inc.; para incluirlas será necesaria la autorización expresa de sus titulares.

Si incorporás materiales de terceros, debés identificar su origen y licencia, y contar con las autorizaciones correspondientes. El permiso especial para Global Game Jam no se extiende a esos materiales sin autorización de sus titulares.

Las condiciones completas se encuentran en [`LICENSE`](LICENSE), [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md) y [`docs/licencia.md`](docs/licencia.md).
