# GGJ Argentina

Sitio colaborativo para reunir la memoria, las experiencias y los recursos de la comunidad de Global Game Jam en Argentina.

El contenido se escribe en Markdown y se publica con [MkDocs](https://www.mkdocs.org/) y [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Ver el sitio localmente

Necesitás Python 3.10 o posterior.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdocs serve
```

Abrí `http://127.0.0.1:8000` en el navegador. Para comprobar que el sitio compila:

```bash
mkdocs build --strict
```

## Contribuir

Las correcciones, recuerdos, fotografías autorizadas y guías son bienvenidas. Leé [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar un cambio. No hace falta saber programación: también podés editar una página desde GitHub con el enlace de edición del sitio.

## Publicación

Los cambios incorporados a `main` se compilan y publican automáticamente mediante GitHub Actions. La primera vez, una persona con permisos de administración debe elegir **GitHub Actions** como fuente en **Settings → Pages**.

## Licencia

La comunidad todavía debe elegir y aprobar la licencia del contenido y, si corresponde, la del código. Hasta que exista un archivo `LICENSE`, no debe asumirse permiso para reutilizar el material. Consultá [docs/licencia.md](docs/licencia.md).
