import os
import re
import tomllib
from pathlib import Path
import typer

CONFIG_DIR = Path.home() / ".decidoc"
CONFIG_FILE = CONFIG_DIR / "config.toml"

def validate_path(path: Path) -> Path:
    absolute_path = os.path.abspath(path)
    
    if not absolute_path.endswith(".md"):
        absolute_path = absolute_path + ".md"
    
    return Path(absolute_path)


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