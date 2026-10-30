"""Genera las páginas públicas e índices de Zensical desde los datos del proyecto.

Las advertencias de edición se mantienen como comentarios HTML invisibles; el
texto público contiene únicamente información destinada a lectores del sitio.
"""

from collections import defaultdict
from pathlib import Path
import html
import re

import yaml


FLAGS = {
    "AR": ("🇦🇷", "Argentina"),
    "BE": ("🇧🇪", "Bélgica"),
    "BR": ("🇧🇷", "Brasil"),
    "CA": ("🇨🇦", "Canadá"),
    "CN": ("🇨🇳", "China"),
    "CO": ("🇨🇴", "Colombia"),
    "DE": ("🇩🇪", "Alemania"),
    "ES": ("🇪🇸", "España"),
    "FI": ("🇫🇮", "Finlandia"),
    "FR": ("🇫🇷", "Francia"),
    "GB": ("🇬🇧", "Reino Unido"),
    "IL": ("🇮🇱", "Israel"),
    "IN": ("🇮🇳", "India"),
    "LV": ("🇱🇻", "Letonia"),
    "LK": ("🇱🇰", "Sri Lanka"),
    "NL": ("🇳🇱", "Países Bajos"),
    "PT": ("🇵🇹", "Portugal"),
    "PK": ("🇵🇰", "Pakistán"),
    "SA": ("🇸🇦", "Arabia Saudita"),
    "TR": ("🇹🇷", "Turquía"),
    "TW": ("🇹🇼", "Taiwán"),
    "UA": ("🇺🇦", "Ucrania"),
    "US": ("🇺🇸", "Estados Unidos"),
}

GENERATED = "<!-- Generado automáticamente desde data/. No editar esta página. -->\n\n"

ROLE_BADGES = {
    "SO": "Site Organizer",
    "RO": "Regional Organizer",
    "EC": "Executive Committee",
}


def _load(path):
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _write(path, content):
    content = GENERATED + content.rstrip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _number(value):
    return f"{value:,}".replace(",", ".")


def _flag(code):
    try:
        emoji, country = FLAGS[code]
    except KeyError as error:
        raise ValueError(f"Código de país desconocido: {code}") from error
    return f'<span class="country-flag" title="{country}" aria-label="{country}">{emoji}</span>'


def _role_badges(codes):
    unique = list(dict.fromkeys(code for code in codes if code in ROLE_BADGES))
    return " ".join(
        f'<span class="role-badge role-badge--{code.lower()}" '
        f'title="{ROLE_BADGES[code]}" aria-label="{ROLE_BADGES[code]}">'
        f'<span class="role-badge__icon" aria-hidden="true"></span>{code}</span>'
        for code in unique
    )


def _role_codes(role):
    if role in {"Organización local", "Site Organizer"}:
        return ["SO"]
    if role in {"Organización regional", "Regional Organizer"}:
        return ["RO"]
    if role == "Executive Committee":
        return ["EC"]
    return []


def _person(person, profile_prefix="../../../personas/", role_codes=()):
    flags = " ".join(_flag(code) for code in person.get("countries", []))
    name = _cell(person["name"])
    if person.get("person_id"):
        name = f"[{name}]({profile_prefix}{person['person_id']}.md)"
    badges = _role_badges(role_codes)
    return " ".join(part for part in (flags, name, badges) if part).strip()


def _site_link(site, prefix="../../../sedes/fichas/"):
    return f"[{_cell(site['name'])}]({prefix}{site['id']}.md)"


def _validate_site(site, path):
    for field in ("id", "year", "name", "province", "locality", "audience", "organization_id", "source"):
        if field not in site or site[field] in (None, ""):
            raise ValueError(f"{path}: falta el campo obligatorio '{field}'")
    if site["audience"] not in {"ggj", "next"}:
        raise ValueError(f"{path}: audience debe ser 'ggj' o 'next'")
    for field in ("participants", "games"):
        value = site.get(field)
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f"{path}: {field} debe ser un entero no negativo")


def _resolve_people(value, people):
    if isinstance(value, list):
        return [_resolve_people(item, people) for item in value]
    if not isinstance(value, dict):
        return value
    resolved = {key: _resolve_people(item, people) for key, item in value.items()}
    person_id = resolved.get("person_id")
    if person_id:
        if person_id not in people:
            raise ValueError(f"Persona desconocida: {person_id}")
        return {**people[person_id], **resolved}
    return resolved


def _reported_summary(sites, field, label):
    reported = [site[field] for site in sites if site.get(field) is not None]
    if not reported:
        return f"Sin cifras reportadas ({label.lower()})"
    return f"{sum(reported):,}".replace(",", ".") + f" ({len(reported)} de {len(sites)} sedes informaron)"


def _share(part, whole):
    return f"{part / whole * 100:.1f}".replace(".", ",")


def _breadcrumb(items):
    links = []
    for label, target in items:
        links.append(f"[{label}]({target})" if target else label)
    return [
        '<nav class="content-breadcrumb" aria-label="Ruta de navegación" markdown>',
        '<span class="content-breadcrumb__separator" aria-hidden="true">›</span>'.join(links),
        "</nav>",
        "",
    ]


def _argentine_participation(edition):
    people = {}

    def add(person, role, scope, source):
        if "AR" not in person.get("countries", []):
            return
        entry = people.setdefault(person["name"], {"person": person, "roles": []})
        item = (role, scope, source)
        if item not in entry["roles"]:
            entry["roles"].append(item)

    for person in edition.get("regional_organizers", []):
        add(person, person["role"], person["scope"], person["source"])
    for person in edition.get("staff", []):
        add(person, person["role"], f"Staff {edition['year']}", "Global Game Jam")
    for person in edition.get("global_regional_coordination", {}).get("members", []):
        add(person, person.get("role", "Global Regional Coordination Team"), str(edition["year"]), edition["global_regional_coordination"]["source"])
    for committee in edition.get("committees", []):
        if committee.get("chair"):
            add(committee["chair"], f"Chair, {committee['title']}", committee.get("period", str(edition["year"])), committee["source"])
        for person in committee.get("members", []):
            add(person, committee["title"], committee.get("period", str(edition["year"])), committee["source"])
    for person in edition.get("executive_committee", {}).get("members", []):
        add(person, "Executive Committee", edition["executive_committee"]["period"], "Global Game Jam")
    for board_key, label in (("board_during", "Board of Directors"), ("board_update", "Board of Directors")):
        board = edition.get(board_key, {})
        for person in board.get("members", []):
            add(person, f"{person['role']}, {label}", board.get("period", str(edition["year"])), "Global Game Jam")
    return [people[name] for name in sorted(people, key=str.casefold)]


def _edition_videos(edition):
    videos = edition.get("videos", [])
    if not videos:
        return []
    lines = ["## Videos de la edición", ""]
    for video in videos:
        video_id = video["youtube_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError(f"ID de video de YouTube inválido: {video_id}")
        title = html.escape(video["title"], quote=True)
        lines += [f"### {_cell(video['title'])}", ""]
        if video.get("description"):
            lines += [video["description"], ""]
        lines += [
            '<div class="edition-video">',
            f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
            f'title="{title}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; '
            'encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>',
            '</div>',
            "",
            f"[Ver en YouTube](https://www.youtube.com/watch?v={video_id})",
            "",
        ]
    return lines


def _render_year(edition, sites):
    year = edition["year"]
    breadcrumb = _breadcrumb([
        ("Inicio", "../../../index.md"),
        ("Historia", "../../index.md"),
        ("Ediciones", "../index.md"),
        (str(year), None),
    ])
    if edition.get("status") == "historica":
        stats = edition.get("global_stats", {})
        lines = breadcrumb + [f"# Edición {year}", ""]
        if edition.get("intro"):
            lines += [edition["intro"], ""]
        lines += ["## Resumen", "", "| Dato | Resultado |", "| --- | --- |"]
        if edition.get("dates"):
            lines.append(f"| Fechas | {_cell(edition['dates'])} |")
        if edition.get("theme"):
            theme = edition['theme']
            translation = f" ({_cell(theme['translation'])})" if theme.get('translation') else ""
            lines.append(f"| Tema | {_cell(theme['name'])}{translation} |")
        for key, label in (("sites", "Sedes"), ("countries", "Países"), ("participants", "Participantes"), ("games", "Juegos")):
            if key in stats:
                lines.append(f"| {label} | {_number(stats[key])} |")
        if sites:
            ggj = [site for site in sites if site['audience'] == 'ggj']
            nxt = [site for site in sites if site['audience'] == 'next']
            lines.append(f"| Sedes GGJ en Argentina | {len(ggj)} |")
            if stats.get('sites'):
                lines.append(f"| Sedes argentinas sobre el total global | {_share(len(ggj), stats['sites'])} % |")
            for key, label, global_key in (('participants', 'Miembros registrados', 'participants'), ('games', 'Juegos', 'games')):
                known = [site[key] for site in ggj if site.get(key) is not None]
                if known:
                    lines.append(f"| {label} en sedes argentinas | {_reported_summary(ggj, key, label)} |")
                    if stats.get(global_key):
                        qualifier = ' (cobertura parcial)' if len(known) < len(ggj) else ''
                        lines.append(f"| {label} sobre el total global | {_share(sum(known), stats[global_key])} %{qualifier} |")
            lines.append(f"| Sedes GGJ NEXT en Argentina | {len(nxt)}, contabilizadas aparte |")
            lines += ["", "Los miembros registrados en las fichas oficiales no equivalen necesariamente a asistencia presencial."]
        if edition.get('regional_organizers'):
            lines += ['', '## Organización regional en Argentina', '']
            for person in edition['regional_organizers']:
                lines.append(f"- {_person(person, role_codes=['RO'])} — {_cell(person['scope'])}")
        if edition.get('staff') or edition.get('executive_committee') or edition.get('committees') or edition.get('board_during'):
            lines += ['', '## Equipo internacional', '']
        if edition.get('staff'):
            staff_period = f" — {_cell(edition['staff_period'])}" if edition.get('staff_period') else ''
            lines += [f'### Staff{staff_period}', '']
            for person in edition['staff']:
                lines.append(f"- {_person(person)} — {_cell(person['role'])}")
            lines.append('')
        if edition.get('executive_committee', {}).get('members'):
            committee = edition['executive_committee']
            lines += [f"### Executive Committee {committee['period']}", '']
            lines += [f"- {_person(person, role_codes=['EC'])}" for person in committee['members']]
            lines.append('')
        for committee in edition.get('committees', []):
            period = f" — {_cell(committee['period'])}" if committee.get('period') else ''
            lines += [f"### {committee['title']}{period}", '']
            if committee.get('coordinator'):
                lines.append(f"- **Coordinación:** {_person(committee['coordinator'])}")
            if committee.get('chair'):
                lines.append(f"- **Chair:** {_person(committee['chair'])}")
            lines += [f"- {_person(person)}" for person in committee.get('members', [])]
            lines.append('')
        for key, title in (('board_during', 'Board of Directors durante la edición'), ('board_update', 'Actualización del Board')):
            board = edition.get(key, {})
            if board.get('members'):
                lines += [f"### {title}", '', board.get('note', ''), '', '| Cargo | Persona |', '| --- | --- |']
                lines += [f"| {_cell(person['role'])} | {_person(person)} |" for person in board['members']]
                lines.append('')
        participation = _argentine_participation(edition)
        if participation:
            lines += ['## Participación argentina', '', '| Persona | Participación | Alcance |', '| --- | --- | --- |']
            for entry in participation:
                roles = '<br>'.join(_cell(item[0]) for item in entry['roles'])
                scopes = '<br>'.join(_cell(item[1]) for item in entry['roles'])
                codes = [code for role, _scope, _source in entry['roles'] for code in _role_codes(role)]
                lines.append(f"| {_person(entry['person'], role_codes=codes)} | {roles} | {scopes} |")
            lines.append('')
        lines += _edition_videos(edition)
        if edition.get('survey_note'):
            lines += ['## Alcance global', '', edition['survey_note'], '']
        if sites:
            lines += ["## Sedes en Argentina", "", "- [Por provincia](sedes-por-provincia.md)", "- [Por nombre](sedes-por-nombre.md)", ""]
        lines += ["", "## Fuentes", ""]
        lines += [f"- [{source['title']}]({source['url']})" for source in edition.get('sources', [])]
        return "\n".join(lines)
    if edition.get("status") == "en_preparacion":
        lines = breadcrumb + [
            f"# Edición {year}",
            "",
            edition["intro"],
            "",
            "## Resumen",
            "",
            "| Dato | Estado |",
            "| --- | --- |",
            "| Edición | En preparación |",
        ]
        if edition.get("dates"):
            lines.append(f"| Fechas globales | {_cell(edition['dates'])} |")
        if edition.get("theme"):
            theme = edition["theme"]
            translation = f" ({_cell(theme['translation'])})" if theme.get("translation") else ""
            lines.append(f"| Tema | **{_cell(theme['name'])}**{translation} |")
        if edition.get("regional_organizers"):
            lines += [
                "",
                "## Organización regional en Argentina",
                "",
                "| Rol | Persona | Período o alcance | Fuente |",
                "| --- | --- | --- | --- |",
            ]
            for person in edition["regional_organizers"]:
                lines.append(
                    f"| {_cell(person['role'])} | {_person(person, role_codes=['RO'])} | "
                    f"{_cell(person['scope'])} | {_cell(person['source'])} |"
                )
        if edition.get("executive_committee", {}).get("members"):
            lines += ["", "## Equipo internacional", "", "### Executive Committee", ""]
            lines += [
                f"- {_person(person, role_codes=['EC'])}"
                for person in edition["executive_committee"]["members"]
            ]
        lines += [""] + _edition_videos(edition)
        if edition.get("sources"):
            lines += ["", "## Fuentes", ""]
            lines += [f"- [{source['title']}]({source['url']})" for source in edition["sources"]]
        return "\n".join(lines)

    ggj_sites = [site for site in sites if site["audience"] == "ggj"]
    next_sites = [site for site in sites if site["audience"] == "next"]
    global_sites = edition["global_stats"]["sites"]
    share = len(ggj_sites) / global_sites * 100
    share_text = f"{share:.1f}".replace(".", ",")
    local_participants = sum(site["participants"] for site in ggj_sites if site.get("participants") is not None)
    local_games = sum(site["games"] for site in ggj_sites if site.get("games") is not None)
    participant_share = _share(local_participants, edition["global_stats"]["participants"])
    games_share = _share(local_games, edition["global_stats"]["games"])

    lines = breadcrumb + [
        f"# Edición {year}",
        "",
        edition["intro"],
        "",
        "## Resumen",
        "",
        "| Dato | Resultado |",
        "| --- | --- |",
        f"| Fechas globales | {_cell(edition['dates'])} |",
        f"| Tema | **{_cell(edition['theme']['name'])}** ({_cell(edition['theme']['translation'])}) |",
        f"| Participantes globales | {_number(edition['global_stats']['participants'])} |",
        f"| Sedes globales | {_number(global_sites)}, incluidas las virtuales |",
        f"| Países | {edition['global_stats']['countries']} |",
        f"| Juegos publicados globalmente | {_number(edition['global_stats']['games'])} |",
        f"| Sedes GGJ registradas en {_flag('AR')} | {len(ggj_sites)} |",
        f"| Participación argentina sobre las sedes globales | **{share_text} %** ({len(ggj_sites)} de {global_sites}) |",
        f"| Miembros registrados en sedes argentinas | {_reported_summary(ggj_sites, 'participants', 'Miembros')} |",
        f"| Participación argentina sobre participantes globales | **{participant_share} %** ({_number(local_participants)} de {_number(edition['global_stats']['participants'])}) |",
        f"| Juegos publicados por sedes argentinas | {_reported_summary(ggj_sites, 'games', 'Juegos')} |",
        f"| Participación argentina sobre juegos globales | **{games_share} %** ({_number(local_games)} de {_number(edition['global_stats']['games'])}) |",
        f"| Sedes GGJ NEXT identificadas en {_flag('AR')} | {len(next_sites)}, contabilizadas aparte |",
        "",
        edition["stats_note"],
        "",
        "Las cifras argentinas de participantes corresponden a integrantes registrados en las fichas oficiales de GGJ; no equivalen necesariamente a asistencia presencial.",
        "",
        "## Organización regional en Argentina",
        "",
        "| Rol | Persona | Período o alcance | Fuente |",
        "| --- | --- | --- | --- |",
    ]
    for person in edition["regional_organizers"]:
        lines.append(f"| {_cell(person['role'])} | {_person(person, role_codes=['RO'])} | {_cell(person['scope'])} | {_cell(person['source'])} |")

    lines += ["", "## Equipo internacional", "", "### Staff", "", "| Cargo | Persona |", "| --- | --- |"]
    for person in edition["staff"]:
        lines.append(f"| {_cell(person['role'])} | {_person(person)} |")

    lines += ["", "### Global Regional Coordination Team", ""]
    for person in edition["global_regional_coordination"]["members"]:
        role = f" — {_cell(person['role'])}" if person.get("role") else ""
        lines.append(f"- {_person(person)}{role}")

    lines += ["", f"### Executive Committee {edition['executive_committee']['period']}", ""]
    lines += [f"- {_person(person, role_codes=['EC'])}" for person in edition["executive_committee"]["members"]]

    for committee in edition.get("committees", []):
        lines += ["", f"### {committee['title']}", ""]
        if committee.get("chair"):
            lines.append(f"- **Chair:** {_person(committee['chair'])}")
        lines += [f"- {_person(person)}" for person in committee.get("members", [])]

    lines += [
        "",
        "### Board of Directors durante la edición",
        "",
        edition["board_during"]["note"],
        "",
        "| Cargo | Persona |",
        "| --- | --- |",
    ]
    for person in edition["board_during"]["members"]:
        lines.append(f"| {_cell(person['role'])} | {_person(person)} |")

    lines += ["", "### Actualización del Board", "", edition["board_update"]["note"], "", "| Cargo | Persona |", "| --- | --- |"]
    for person in edition["board_update"]["members"]:
        lines.append(f"| {_cell(person['role'])} | {_person(person)} |")

    lines += ["", "## Participación argentina", "", "| Persona | Participación | Alcance |", "| --- | --- | --- |"]
    for entry in _argentine_participation(edition):
        roles = "<br>".join(_cell(item[0]) for item in entry["roles"])
        scopes = "<br>".join(_cell(item[1]) for item in entry["roles"])
        codes = [code for role, _scope, _source in entry["roles"] for code in _role_codes(role)]
        lines.append(f"| {_person(entry['person'], role_codes=codes)} | {roles} | {scopes} |")

    lines += [""] + _edition_videos(edition)
    lines += [
        "",
        f"## Tema: {edition['theme']['name']}",
        "",
        edition["theme"]["note"],
        "",
        "## Sedes argentinas",
        "",
        f"El inventario contiene **{len(ggj_sites)} sedes de la GGJ principal** en {_flag('AR')}. Representan aproximadamente el **{share_text} % de las {global_sites} sedes globales**.",
        "",
        "- [Agrupadas por provincia](sedes-por-provincia.md)",
        "- [Ordenadas por nombre](sedes-por-nombre.md)",
        "",
        f"Además hay **{len(next_sites)} sedes GGJ NEXT** registradas por separado. GGJ NEXT no se suma al porcentaje anterior porque la organización la excluye de los totales de la GGJ principal.",
        "",
        "## Alcance global",
        "",
        edition["survey_note"],
        "",
        "## Fuentes",
        "",
    ]
    lines += [f"- [{source['title']}]({source['url']})" for source in edition["sources"]]
    lines += ["- Capturas de los créditos del keynote de GGJ 2026 aportadas por la comunidad."]
    return "\n".join(lines)


def _render_year_sites(year, sites, group_by_province):
    ggj_sites = sorted((s for s in sites if s["audience"] == "ggj"), key=lambda s: s["name"].casefold())
    next_sites = sorted((s for s in sites if s["audience"] == "next"), key=lambda s: s["name"].casefold())
    mode = "provincia" if group_by_province else "nombre"
    lines = _breadcrumb([
        ("Inicio", "../../../index.md"),
        ("Historia", "../../index.md"),
        ("Ediciones", "../index.md"),
        (str(year), "index.md"),
        (f"Sedes por {mode}", None),
    ]) + [f"# Sedes de {year} por {mode}", "", f"Este índice reúne **{len(ggj_sites)} sedes GGJ** de Argentina.", ""]
    if group_by_province:
        groups = defaultdict(list)
        for site in ggj_sites:
            groups[site["province"]].append(site)
        for province in sorted(groups, key=str.casefold):
            lines += [f"## {province}", ""]
            for site in sorted(groups[province], key=lambda s: (s["locality"].casefold(), s["name"].casefold())):
                lines.append(f"- {_site_link(site)} — {_cell(site['locality'])}")
            lines.append("")
    else:
        for site in ggj_sites:
            lines.append(f"- {_site_link(site)} — {_cell(site['locality'])}, {_cell(site['province'])}")
        lines.append("")
    lines += ["## GGJ NEXT", ""]
    for site in next_sites:
        lines.append(f"- {_site_link(site)} — {_cell(site['locality'])}, {_cell(site['province'])}")
    return "\n".join(lines)


def _render_editions_index(editions):
    lines = [
        "# Ediciones por año",
        "",
        "Cada edición reúne su contexto, organización regional, estructura internacional, participación argentina y sedes.",
        "",
    ]
    for year in sorted(editions, reverse=True):
        edition = editions[year]
        if edition.get("theme"):
            detail = edition["theme"]["name"]
            if edition["theme"].get("translation"):
                detail += f" ({_cell(edition['theme']['translation'])})"
        elif edition.get("status") == "en_preparacion":
            detail = "En preparación"
        else:
            detail = "Edición documentada"
        lines.append(f"- [{year}]({year}/index.md) — {detail}")
    return "\n".join(lines)


def _render_sites_index(sites):
    editions = len({site["year"] for site in sites})
    organizations = len({site["organization_id"] for site in sites})
    edition_label = "edición" if editions == 1 else "ediciones"
    organization_label = "organización" if organizations == 1 else "organizaciones"
    lines = [
        "# Sedes",
        "",
        f"El directorio reúne **{len(sites)} eventos**, correspondientes a **{organizations} {organization_label}** en **{editions} {edition_label}**.",
        "",
        "- [Por provincia](por-provincia.md)",
        "- [Por nombre](por-nombre.md)",
        "- [Organizaciones](../organizaciones/index.md)",
    ]
    return "\n".join(lines)


def _event_links(events, prefix=""):
    return ", ".join(
        f"[{event['name']}]({prefix}{event['id']}.md)" for event in events
    )


def _render_site(site, organization, previous_events, next_events, people):
    lines = _breadcrumb([
        ("Inicio", "../../index.md"),
        ("Sedes", "../index.md"),
        (_cell(site["name"]), None),
    ]) + [
        f"# {site['name']}",
        "",
        "| Dato | Valor |",
        "| --- | --- |",
        f"| Edición | [{site['year']}](../../historia/anios/{site['year']}/index.md) |",
        f"| Modalidad | {'GGJ' if site['audience'] == 'ggj' else 'GGJ NEXT'} |",
        f"| Localidad | {_cell(site['locality'])} |",
        f"| Provincia | {_cell(site['province'])} |",
        f"| Organización | [{_cell(organization['name'])}](../../organizaciones/fichas/{organization['id']}.md) |",
        f"| {'Miembros registrados en GGJ' if site.get('participants_basis') == 'registered_members' else 'Participantes'} | {site.get('participants', '—')} |",
        f"| Juegos | {site.get('games', '—')} |",
    ]
    if site.get("format"):
        lines.append(f"| Formato | {_cell(site['format'])} |")
    if site.get("organizers"):
        lines += ["", "## Organización local", ""]
        for organizer in site["organizers"]:
            if isinstance(organizer, dict) and organizer.get("person_id"):
                person = people[organizer["person_id"]]
                lines.append(f"- [{_cell(person['name'])}](../../personas/{person['id']}.md) {_role_badges(['SO'])}")
            else:
                lines.append(f"- {_cell(organizer)} {_role_badges(['SO'])}")
    if site.get("notes"):
        lines += ["", "## Notas", "", site["notes"]]
    lines += ["", "## Fuente", "", f"- [Fuente de la ficha]({site['source']})"]
    if site.get("participants_source"):
        lines.append(f"- [Miembros registrados]({site['participants_source']})")
    if site.get("games_source"):
        lines.append(f"- [Juegos de la sede]({site['games_source']})")
    if previous_events or next_events:
        lines += ["", "## Otras ediciones de la organización", ""]
        if previous_events:
            lines.append(f"- **Anterior:** {_event_links(previous_events)}")
        if next_events:
            lines.append(f"- **Siguiente:** {_event_links(next_events)}")
    return "\n".join(lines)


def _render_organization(organization, events):
    lines = _breadcrumb([
        ("Inicio", "../../index.md"),
        ("Organizaciones", "../index.md"),
        (_cell(organization["name"]), None),
    ]) + [
        f"# {organization['name']}",
        "",
    ]
    if organization.get("summary"):
        lines += [organization["summary"], ""]
    lines += ["## Participaciones documentadas", ""]
    for event in sorted(events, key=lambda item: (item["year"], item["locality"].casefold())):
        lines.append(
            f"- [{event['year']} — {event['name']}](../../sedes/fichas/{event['id']}.md) — "
            f"{event['locality']}, {event['province']}"
        )
    if organization.get("website") or organization.get("source"):
        lines += ["", "## Enlaces", ""]
        if organization.get("website"):
            lines.append(f"- [Sitio web]({organization['website']})")
        if organization.get("source"):
            lines.append(f"- [Fuente]({organization['source']})")
    return "\n".join(lines)


def _render_organizations_index(organizations, sites):
    counts = defaultdict(int)
    for site in sites:
        counts[site["organization_id"]] += 1
    lines = ["# Organizaciones", ""]
    for organization in sorted(organizations.values(), key=lambda item: item["name"].casefold()):
        count = counts[organization["id"]]
        label = "participación" if count == 1 else "participaciones"
        lines.append(
            f"- [{organization['name']}](fichas/{organization['id']}.md) — {count} {label} documentadas"
        )
    return "\n".join(lines)


def _regional_assignments(editions, regional_records):
    assignments = []
    for year, edition in editions.items():
        for person in edition.get("regional_organizers", []):
            assignments.append((year, person))
    for year, record in regional_records.items():
        for person in record.get("regional_organizers", []):
            item = (year, person)
            if item not in assignments:
                assignments.append(item)
    return sorted(assignments, key=lambda item: item[0])


def _person_roles(person_id, editions, regional_records, sites):
    roles = []

    def add(year, role, site=None):
        item = {"year": year, "role": role, "site": site}
        key = (year, role, site["id"] if site else None)
        existing = {
            (entry["year"], entry["role"], entry["site"]["id"] if entry["site"] else None)
            for entry in roles
        }
        if key not in existing:
            roles.append(item)

    for year, edition in sorted(editions.items()):
        for entry in _argentine_participation(edition):
            if entry["person"].get("person_id") != person_id:
                continue
            for role, _scope, _source in entry["roles"]:
                add(year, role)
    for year, person in _regional_assignments(editions, regional_records):
        if person.get("person_id") != person_id:
            continue
        add(year, person["role"])
    for site in sites:
        for organizer in site.get("organizers", []):
            if isinstance(organizer, dict) and organizer.get("person_id") == person_id:
                add(site["year"], "Organización local", site)
    roles.sort(key=lambda item: item["year"])
    return roles


def _person_organizations(person_id, sites, organizations):
    related = {}
    for site in sites:
        for organizer in site.get("organizers", []):
            if isinstance(organizer, dict) and organizer.get("person_id") == person_id:
                related[site["organization_id"]] = organizations[site["organization_id"]]
    return list(related.values())


def _render_person(person, roles, organizations, editions):
    person_codes = [code for entry in roles for code in _role_codes(entry["role"])]
    lines = _breadcrumb([
        ("Inicio", "../index.md"),
        ("Personas", "index.md"),
        (_cell(person["name"]), None),
    ]) + [f"# {_flag('AR')} {person['name']} {_role_badges(person_codes)}", ""]
    if person.get("photo"):
        lines += [f"![Foto de {_cell(person['name'])}]({person['photo']}){{ width=\"240\" }}", ""]
    biography = person.get("bio") or person.get("summary")
    if biography:
        lines += [biography, ""]
    if roles:
        grouped = defaultdict(list)
        for entry in roles:
            if entry["site"]:
                site = entry["site"]
                label = (
                    f"{_cell(entry['role'])} {_role_badges(_role_codes(entry['role']))} — "
                    f"[{_cell(site['name'])}](../sedes/fichas/{site['id']}.md)"
                )
            else:
                label = f"{_cell(entry['role'])} {_role_badges(_role_codes(entry['role']))}".strip()
            if label not in grouped[entry["year"]]:
                grouped[entry["year"]].append(label)
        lines += [
            "## Participación en Global Game Jam",
            "",
            "| Edición | Participación |",
            "| --- | --- |",
        ]
        for year in sorted(grouped):
            edition = f"[{year}](../historia/anios/{year}/index.md)" if year in editions else str(year)
            lines.append(f"| {edition} | {'<br>'.join(grouped[year])} |")
    if organizations:
        lines += ["", "## Organizaciones", ""]
        for organization in sorted(organizations, key=lambda item: item["name"].casefold()):
            lines.append(f"- [{organization['name']}](../organizaciones/fichas/{organization['id']}.md)")
    links = []
    if person.get("website"):
        links.append(("Sitio web", person["website"]))
    for link in person.get("links", []):
        links.append((link["label"], link["url"]))
    if links:
        lines += ["", "## Enlaces", ""]
        for label, url in links:
            lines.append(f"- [{_cell(label)}]({url})")
    if person.get("sources"):
        lines += ["", "## Fuentes", ""]
        for source in person["sources"]:
            lines.append(f"- [{source['title']}]({source['url']})")
    return "\n".join(lines)


def _render_people_index(people, editions, regional_records, sites):
    lines = ["# Personas", ""]
    for person in sorted(people.values(), key=lambda item: item["name"].casefold()):
        roles = _person_roles(person["id"], editions, regional_records, sites)
        latest = max((role["year"] for role in roles), default=None)
        suffix = f" — actividad documentada hasta {latest}" if latest else ""
        codes = [code for role in roles for code in _role_codes(role["role"])]
        lines.append(f"- [{_flag('AR')} {person['name']}]({person['id']}.md) {_role_badges(codes)}{suffix}")
    return "\n".join(lines)


def _render_regional_organizers(editions, regional_records):
    grouped = defaultdict(list)
    for year, person in _regional_assignments(editions, regional_records):
        grouped[year].append(person)
    lines = ["# Organización regional", ""]
    for year in sorted(grouped, reverse=True):
        lines += [f"## {year}", ""]
        for person in grouped[year]:
            lines.append(f"- {_person(person, '../personas/', ['RO'])}")
        lines.append("")
    return "\n".join(lines)


def _render_global_sites(sites, group_by_province):
    ggj_sites = [site for site in sites if site["audience"] == "ggj"]
    title = "Sedes por provincia" if group_by_province else "Sedes por nombre"
    lines = [f"# {title}", "", f"El directorio reúne **{len(ggj_sites)} participaciones de sedes GGJ documentadas**.", ""]
    if group_by_province:
        groups = defaultdict(list)
        for site in ggj_sites:
            groups[site["province"]].append(site)
        for province in sorted(groups, key=str.casefold):
            lines += [f"## {province}", ""]
            for site in sorted(groups[province], key=lambda s: s["name"].casefold()):
                lines.append(f"- {_site_link(site, 'fichas/')} — {site['locality']} ({site['year']})")
            lines.append("")
    else:
        for site in sorted(ggj_sites, key=lambda s: s["name"].casefold()):
            lines.append(f"- {_site_link(site, 'fichas/')} — {site['locality']}, {site['province']} ({site['year']})")
    return "\n".join(lines)


def generate(root=None):
    """Regenera las páginas derivadas de los archivos YAML del proyecto."""
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    docs = root / "docs"
    edition_files = sorted((root / "data" / "editions").glob("*.yml"))
    site_files = sorted((root / "data" / "sites").glob("*/*.yml"))
    organization_files = sorted((root / "data" / "organizations").glob("*.yml"))
    people_files = sorted((root / "data" / "people").glob("*.yml"))
    regional_files = sorted((root / "data" / "regional_organizers").glob("*.yml"))
    organizations = {_load(path)["id"]: _load(path) for path in organization_files}
    people = {_load(path)["id"]: _load(path) for path in people_files}
    editions = {}
    for path in edition_files:
        edition = _resolve_people(_load(path), people)
        editions[edition["year"]] = edition
    regional_records = {}
    for path in regional_files:
        record = _resolve_people(_load(path), people)
        regional_records[record["year"]] = record
    for year, record in regional_records.items():
        if year in editions and not editions[year].get("regional_organizers"):
            editions[year]["regional_organizers"] = record["regional_organizers"]
    sites = []
    for path in site_files:
        site = _load(path)
        _validate_site(site, path)
        if site["year"] not in editions:
            raise ValueError(f"{path}: no existe data/editions/{site['year']}.yml")
        if site["organization_id"] not in organizations:
            raise ValueError(f"{path}: organización desconocida '{site['organization_id']}'")
        sites.append(site)

    duplicate_ids = {site["id"] for site in sites if sum(other["id"] == site["id"] for other in sites) > 1}
    if duplicate_ids:
        raise ValueError(f"IDs de sede duplicados: {', '.join(sorted(duplicate_ids))}")

    for year, edition in editions.items():
        year_sites = [site for site in sites if site["year"] == year]
        target = docs / "historia" / "anios" / str(year)
        _write(target / "index.md", _render_year(edition, year_sites))
        if year_sites:
            _write(target / "sedes-por-provincia.md", _render_year_sites(year, year_sites, True))
            _write(target / "sedes-por-nombre.md", _render_year_sites(year, year_sites, False))
    _write(docs / "historia" / "anios" / "index.md", _render_editions_index(editions))
    _write(
        docs / "historia" / "organizacion-regional.md",
        _render_regional_organizers(editions, regional_records),
    )

    sites_by_organization = defaultdict(list)
    for site in sites:
        sites_by_organization[site["organization_id"]].append(site)

    for site in sites:
        related = sites_by_organization[site["organization_id"]]
        previous_years = [item["year"] for item in related if item["year"] < site["year"]]
        next_years = [item["year"] for item in related if item["year"] > site["year"]]
        previous_events = [item for item in related if previous_years and item["year"] == max(previous_years)]
        next_events = [item for item in related if next_years and item["year"] == min(next_years)]
        _write(
            docs / "sedes" / "fichas" / f"{site['id']}.md",
            _render_site(
                site,
                organizations[site["organization_id"]],
                previous_events,
                next_events,
                people,
            ),
        )

    for organization_id, organization in organizations.items():
        _write(
            docs / "organizaciones" / "fichas" / f"{organization_id}.md",
            _render_organization(organization, sites_by_organization[organization_id]),
        )
    _write(docs / "organizaciones" / "index.md", _render_organizations_index(organizations, sites))

    for person_id, person in people.items():
        _write(
            docs / "personas" / f"{person_id}.md",
            _render_person(
                person,
                _person_roles(person_id, editions, regional_records, sites),
                _person_organizations(person_id, sites, organizations),
                editions,
            ),
        )
    _write(
        docs / "personas" / "index.md",
        _render_people_index(people, editions, regional_records, sites),
    )
    _write(docs / "sedes" / "index.md", _render_sites_index(sites))
    _write(docs / "sedes" / "por-provincia.md", _render_global_sites(sites, True))
    _write(docs / "sedes" / "por-nombre.md", _render_global_sites(sites, False))
    return None


def on_config(config):
    """Conserva compatibilidad con instalaciones anteriores de MkDocs."""
    generate(Path(config.config_file_path).parent)
    return config


if __name__ == "__main__":
    generate()
