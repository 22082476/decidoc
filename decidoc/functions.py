from typing import Optional
from pathlib import Path
import typer
import re
from decidoc.apa import format_apa
from helper_functions import resolve_path
from datetime import date
from helper_functions import CONFIG_DIR, CONFIG_FILE, validate_path, save_config, get_next_id


def rollback_function(
    path: Optional[Path],
):
    path = resolve_path(path)

    if not path.exists():
        typer.echo("❌ Keuzelog niet gevonden")
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    
    ids = re.findall(r"K-(\d+)", content)
    if not ids:
        typer.echo("⚠️ Geen keuzes gevonden om terug te draaien.")
        raise typer.Exit(0)

    last_id_num = max(map(int, ids))
    last_id = f"K-{last_id_num:03d}"
    
    confirm = typer.confirm(f"⚠️ Weet je zeker dat je keuze {last_id} wilt verwijderen?")
    if not confirm:
        raise typer.Abort()

    lines = content.splitlines()
    
    table_row_start = f"| [{last_id}]"
    lines = [line for line in lines if not line.strip().startswith(table_row_start)]

    section_header = f"## Keuze {last_id}"
    
    start_index = -1
    for i, line in enumerate(lines):
        if section_header in line:
            start_index = i
            break
            
    if start_index != -1:
        
        removal_start = start_index
        for j in range(start_index - 1, max(-1, start_index - 6), -1):
            if lines[j].strip() == "---":
                removal_start = j
                break
        
        removal_end = len(lines)
        for k in range(start_index + 1, len(lines)):
            if lines[k].strip().startswith("## Keuze ") or (lines[k].strip() == "---" and k > start_index + 2):
                 removal_end = k
                 break
        
        del lines[removal_start:removal_end]

    path.write_text("\n".join(lines), encoding="utf-8")
    typer.echo(f"✅ Keuze {last_id} succesvol verwijderd.")

def add_function(
    title: str,
    category: str,
    status: str,
    context: str,
    considerations: str,
    choice: str,
    motivation: str,
    reflection: str,
    stakeholders: str,
    sources: list[str],

    path: Optional[Path],
):
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

def init_function(
    path: Path,
):
    path = validate_path(path)

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