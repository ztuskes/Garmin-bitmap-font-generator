import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt
import sys

console = Console()

def load_api_key(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        console.print(Panel.fit(
            f"[red]Error: API key file '{file_path}' not found.[/red]\n"
            "Please create the file and add your Google Fonts API key.",
            title="API Key Error"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel.fit(
            f"[red]Error reading API key file: {str(e)}[/red]",
            title="API Key Error"
        ))
        sys.exit(1)

def load_characters(file_path):
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            chars = file.read().strip()
            console.print(f"[green]Successfully loaded {len(chars)} characters from {file_path}[/green]")
            return chars
    except FileNotFoundError:
        console.print(Panel.fit(
            f"[red]Error: Character file '{file_path}' not found.[/red]\n"
            "Please create the file with the characters you want to include.",
            title="Character File Error"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel.fit(
            f"[red]Error reading character file: {str(e)}[/red]",
            title="Character File Error"
        ))
        sys.exit(1)

def display_font_options(fonts, title="Available Fonts"):
    table = Table(title=title)
    table.add_column("Option", justify="right", style="cyan")
    table.add_column("Font Name", style="green")
    table.add_column("Available Styles", style="yellow")
    
    for idx, font in enumerate(fonts, 1):
        styles = ", ".join(sorted([
            style for style in [
                "regular" if "regular" in font["files"] else None,
                "bold" if "700" in font["files"] else None,
                "italic" if "italic" in font["files"] else None,
                "bolditalic" if "700italic" in font["files"] else None
            ] if style is not None
        ]))
        table.add_row(str(idx), font["family"], styles)
    
    console.print(table)

def display_style_options(styles, title="Available Styles"):
    table = Table(title=title)
    table.add_column("Option", justify="right", style="cyan")
    table.add_column("Style", style="green")
    
    for idx, style in enumerate(styles, 1):
        table.add_row(str(idx), style)
    
    console.print(table)

def get_available_styles(font):
    style_mapping = {
        'regular': 'regular' in font["files"],
        'bold': '700' in font["files"],
        'italic': 'italic' in font["files"],
        'bolditalic': '700italic' in font["files"]
    }
    return {style: available for style, available in style_mapping.items() if available}