import os
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn
from difflib import get_close_matches
from utils import console, display_font_options
from rich.prompt import IntPrompt
from rich.panel import Panel
import sys
from config import FONT_DOWNLOAD_URL, FONTS_DIR

def find_similar_fonts(search_term, available_fonts, max_results=5):
    """Find fonts with names similar to the search term."""
    font_names = [font["family"] for font in available_fonts]
    exact_matches = [name for name in font_names if search_term.lower() in name.lower()]
    
    if exact_matches:
        return exact_matches[:max_results]
    
    similar_names = get_close_matches(search_term, font_names, n=max_results, cutoff=0.6)
    return similar_names

def get_font_selection(search_term, available_fonts):
    """Present similar font options and get user selection."""
    similar_fonts = []
    for font_name in find_similar_fonts(search_term, available_fonts):
        for font in available_fonts:
            if font["family"] == font_name:
                similar_fonts.append(font)
                break
    
    if not similar_fonts:
        console.print(Panel.fit(
            "[red]No similar fonts found.[/red]\nPlease try a different font name.",
            title="Font Search"
        ))
        sys.exit(1)
    
    console.print(f"\n[yellow]Font '{search_term}' not found. Here are similar options:[/yellow]")
    display_font_options(similar_fonts)
    
    while True:
        try:
            choice = IntPrompt.ask("\nSelect a font number (0 to exit)", default=1)
            if choice == 0:
                console.print("[yellow]Exiting...[/yellow]")
                sys.exit(0)
            if 1 <= choice <= len(similar_fonts):
                return similar_fonts[choice - 1]
            console.print("[red]Invalid choice. Please select a valid number.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Process interrupted by user[/yellow]")
            sys.exit(0)

def get_style_selection(font):
    """Present available font styles and get user selection."""
    available_styles = font.get("variants", [])
    
    if not available_styles:
        console.print(Panel.fit(
            "[red]No styles available for this font.[/red]",
            title="Style Error"
        ))
        sys.exit(1)
    
    if len(available_styles) == 1:
        style = available_styles[0]
        console.print(f"[green]Only one style available: {style}[/green]")
        return style
    
    console.print("\n[yellow]Available styles for this font:[/yellow]")
    for i, style in enumerate(available_styles, 1):
        console.print(f"{i}. {style}")
    
    while True:
        try:
            choice = IntPrompt.ask("\nSelect a style number (0 to exit)", default=1)
            if choice == 0:
                console.print("[yellow]Exiting...[/yellow]")
                sys.exit(0)
            if 1 <= choice <= len(available_styles):
                return available_styles[choice - 1]
            console.print("[red]Invalid choice. Please select a valid number.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Process interrupted by user[/yellow]")
            sys.exit(0)

def download_google_font(font_name, api_key):
    """Download a Google Font and return its file path and details."""
    cleaned_font_name = font_name.replace(" ", "")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        try:
            # Single task for overall progress
            task = progress.add_task("Fetching font information...", total=None)
            
            params = {"key": api_key, "sort": "popularity"}
            response = requests.get(FONT_DOWNLOAD_URL, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve fonts list (HTTP {response.status_code})")
            
            fonts_data = response.json()
            available_fonts = fonts_data.get("items", [])
            
            selected_font = None
            for font in available_fonts:
                if font["family"].lower() == font_name.lower():
                    selected_font = font
                    break
            
            if not selected_font:
                progress.stop()  # Pause progress during selection
                selected_font = get_font_selection(font_name, available_fonts)
                font_name = selected_font["family"]
                progress.start()  # Resume progress
            
            progress.stop()  # Pause for style selection
            console.print("\n[yellow]Please select a font style:[/yellow]")
            font_style = get_style_selection(selected_font)
            progress.start()  # Resume progress
            
            progress.update(task, description=f"Downloading font: {font_name} ({font_style})")
            
            font_file = os.path.join(FONTS_DIR, f"{cleaned_font_name}_{font_style}.ttf")
            if os.path.exists(font_file):
                console.print(f"[green]Found existing font file: {font_file}[/green]")
                return font_file, font_name, font_style
            
            ttf_url = selected_font["files"].get(font_style)
            if not ttf_url:
                raise ValueError(
                    f"Style '{font_style}' is not available for font '{font_name}'\n"
                    f"Available styles: {', '.join(selected_font['files'].keys())}"
                )
            
            os.makedirs(FONTS_DIR, exist_ok=True)
            font_response = requests.get(ttf_url)
            with open(font_file, "wb") as file:
                file.write(font_response.content)
            
            return font_file, font_name, font_style
            
        except requests.RequestException as e:
            console.print(Panel.fit(
                f"[red]Network error while downloading font: {str(e)}[/red]",
                title="Download Error"
            ))
            sys.exit(1)
        except ValueError as e:
            console.print(Panel.fit(f"[red]{str(e)}[/red]", title="Font Error"))
            sys.exit(1)
        except Exception as e:
            console.print(Panel.fit(
                f"[red]Unexpected error: {str(e)}[/red]",
                title="Error"
            ))
            sys.exit(1)