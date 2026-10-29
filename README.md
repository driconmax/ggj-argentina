# GGJ Argentina

Sitio colaborativo para reunir memorias, experiencias y recursos de la comunidad de Global Game Jam en Argentina.

El contenido narrativo se escribe en Markdown. Los datos de ediciones, eventos, organizaciones y personas se guardan en YAML; durante la compilación se generan automáticamente fichas, relaciones, índices y estadísticas. El sitio se publica con [Zensical](https://zensical.org/).

## Ver el sitio localmente

Necesitás Python 3.10 o posterior.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python hooks/site_builder.py
zensical serve
```

Abrí `http://127.0.0.1:8000` en el navegador. Para comprobar que el sitio compila:

```bash
python hooks/site_builder.py
zensical build --strict
```

## Contribuir

Las correcciones, recuerdos, fotografías autorizadas y guías son bienvenidas. Leé [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar un cambio. No hace falta saber programación: también podés editar una página desde GitHub con el enlace de edición del sitio.

Para informar un evento, editá o agregá un archivo dentro de `data/sites/AAAA/`. Los campos opcionales `participants` y `games` alimentan automáticamente los totales, que siempre indican cuántas sedes reportaron cada cifra. Las organizaciones viven en `data/organizations/` y las personas argentinas en `data/people/`; se las relaciona mediante sus identificadores estables. Después de cambiar datos, ejecutá `python hooks/site_builder.py`. No edites las páginas generadas dentro de `docs/sedes/fichas/`, `docs/organizaciones/`, `docs/personas/` o `docs/historia/anios/AAAA/`.

## Publicación

Los cambios incorporados a `main` se compilan y publican automáticamente mediante GitHub Actions.

## Licencia

GGJ Argentina proyecto colaborativo de código abierto.

- **Contenido y documentación:** [Creative Commons BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Se permite compartir, modificar y reutilizar el contenido, incluso comercialmente, siempre que se reconozca la autoría y las adaptaciones mantengan la misma licencia.
- **Código y configuración:** [MIT](https://opensource.org/licenses/MIT). Se permite utilizar, modificar y distribuir libremente el código, conservando los avisos de derechos de autor y licencia.

Quienes acepten expresamente las condiciones de contribución también conceden a Global Game Jam, Inc. el permiso especial detallado en [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md); este permiso no se aplica retroactivamente ni alcanza materiales de terceros.

Las fotografías, logotipos y materiales de terceros conservan sus respectivos derechos y condiciones de uso.

Consultá [Licencia](docs/licencia.md) y [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md) para conocer los términos completos y las condiciones de atribución.

Este proyecto es una iniciativa comunitaria y no representa necesariamente las posiciones oficiales de Global Game Jam, Inc.
