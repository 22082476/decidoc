import typer
from pathlib import Path
from datetime import date
import re
import tomllib
from decidoc.apa import format_apa

app = typer.Typer(help="DeciDoc – Decision Documentation CLI")

CONFIG_DIR = Path.home() / ".decidoc"
CONFIG_FILE = CONFIG_DIR / "config.toml"


# ------------------------
# Config helpers
# ------------------------

def save_config(path: Path):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    print(f'keuzelog_path = "{path.as_posix()}"\n',)
    CONFIG_FILE.write_text(
        f'keuzelog_path = "{path.as_posix()}"\n',
        encoding="utf-8"
    )


def load_config_path() -> Path | None:
    if not CONFIG_FILE.exists():
        return None
    data = tomllib.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return Path(data.get("keuzelog_path"))


# ------------------------
# Utils
# ------------------------

def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def get_next_id(content: str) -> str:
    ids = re.findall(r"K-(\d+)", content)
    next_id = max(map(int, ids)) + 1 if ids else 1
    return f"K-{next_id:03d}"


def resolve_path(path: Path | None) -> Path:
    if path:
        save_config(path)
        return path

    stored = load_config_path()
    if stored:
        return stored

    typer.echo("❌ Geen keuzelog pad ingesteld. Gebruik eerst 'decidoc init'.")
    raise typer.Exit(1)


# ------------------------
# INIT COMMAND
# ------------------------

@app.command()
def init(
    path: Path = typer.Option(..., help="Pad naar het markdown bestand"),
):
    """
    Initialiseert een nieuw keuzelog document en slaat het pad op.
    """
    ensure_parent(path)

    if path.exists():
        typer.echo("❌ Bestand bestaat al")
        raise typer.Exit(1)

    template = """# Keuzelog – Afstudeerstage

Dit document bevat alle belangrijke keuzes die tijdens de afstudeerstage
zijn gemaakt. De overzichtstabel biedt snelle navigatie; per keuze is een
uitgebreide toelichting opgenomen.

## Overzicht gemaakte keuzes

| ID | Datum | Categorie | Omschrijving | Status |
|----|-------|-----------|--------------|--------|

---

## Toelichting per keuze
"""

    path.write_text(template, encoding="utf-8")
    save_config(path)

    typer.echo(f"✅ Keuzelog aangemaakt op {path}")
    typer.echo("📌 Pad opgeslagen voor toekomstig gebruik")


# ------------------------
# ADD COMMAND
# ------------------------

@app.command()
def add(
    title: str = typer.Option(..., help="Korte omschrijving van de keuze"),
    category: str = typer.Option(..., help="Categorie (Architectuur, Ontwerp, etc.)"),
    status: str = typer.Option("Definitief", help="Status van de keuze"),

    context: str = typer.Option("", help="Context van de keuze"),
    considerations: str = typer.Option("", help="Overwogen opties"),
    choice: str = typer.Option("", help="Gemaakte keuze"),
    motivation: str = typer.Option("", help="Motivatie voor de keuze"),
    reflection: str = typer.Option("", help="Eerste reflectie / leerpunt"),
    stakeholders: str = typer.Option("", help="Betrokkenen bij de keuze"),
    sources: list[str] = typer.Option(None, help="Bronverwijzing (URL of tekst) Bijv. -s 'https://www.python.org, https://www.google.com'"),

    path: Path | None = typer.Option(None, help="Optioneel: override pad"),
):
    """
    Voeg een nieuwe keuze toe aan het keuzelog.
    """
    path = resolve_path(path)

    if not path.exists():
        typer.echo("❌ Keuzelog niet gevonden")
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    choice_id = get_next_id(content)
    today = date.today().isoformat()

    anchor = f"keuze-{choice_id.lower()}"

    table_row = (
        f"| [{choice_id}](#{anchor}) | {today} | {category} | {title} | {status} |"
    )

    sources_section = ""
    if sources:
        # Split comma-separated sources and flatten list
        processed_sources = []
        for s in sources:
            if "," in s:
                processed_sources.extend([item.strip() for item in s.split(",")])
            else:
                processed_sources.append(s.strip())

        formatted_sources = []
        with typer.progressbar(processed_sources, label="Initialiseren bronnen...") as progress:
            for s in progress:
                formatted_sources.append(format_apa(s))
        
        sources_list = "\n".join([f"- {s}" for s in formatted_sources])
        sources_section = f"{sources_list}"


    section = f"""
---

## Keuze {choice_id} – {title}
<a id="{anchor}"></a>

**Datum:** {today}  
**Categorie:** {category}  
**Betrokkenen:**  {stakeholders}

### Context
{context or "Nog in te vullen."}

### Overwegingen
{considerations or "Nog in te vullen."}

### Gemaakte keuze
{choice or "Nog in te vullen."}

### Motivatie
{motivation or "Nog in te vullen."}

### Eerste reflectie
{reflection or "Nog in te vullen."}

### Bronnen
{sources_section or "Nog in te vullen."}
"""

    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|----"):
            lines.insert(i + 1, table_row)
            break

    updated = "\n".join(lines) + section
    path.write_text(updated, encoding="utf-8")

    typer.echo(f"✅ Keuze {choice_id} toegevoegd")


# ------------------------
# SHOW CONFIG (handig)
# ------------------------

@app.command()
def config():
    """
    Toon het opgeslagen keuzelog pad.
    """
    path = load_config_path()
    if path:
        typer.echo(f"📄 Huidig keuzelog: {path}")
    else:
        typer.echo("❌ Nog geen keuzelog pad ingesteld")


def main():
    app()

if __name__ == "__main__":
    main()