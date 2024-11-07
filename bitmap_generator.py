from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import os
import shutil
from rich.progress import Progress
from utils import console, load_api_key, load_characters
from rich.panel import Panel
import sys
import numpy as np
from config import (
    API_KEY_FILE, CHAR_FILE, OUTPUT_DIR, SIZES,
    BASE_RESOLUTION, MAX_ROW_WIDTH
)
from font_manager import download_google_font

def find_char_boundaries(img):
    """Find the actual character boundaries by analyzing pixel data"""
    data = np.array(img)
    non_empty_columns = np.where(data.sum(axis=0) > 0)[0]
    non_empty_rows = np.where(data.sum(axis=1) > 0)[0]
    
    if len(non_empty_columns) == 0 or len(non_empty_rows) == 0:
        return 0, 0, 0, 0
        
    left = non_empty_columns[0]
    right = non_empty_columns[-1] + 1
    top = non_empty_rows[0]
    bottom = non_empty_rows[-1] + 1
    
    return left, top, right, bottom

def render_character(char, font, padding=0):
    """Render a single character and find its true boundaries"""
    # Create an image 3x the font size to ensure enough space
    font_size = font.size
    temp_img = Image.new('L', (font_size * 3, font_size * 3), 0)
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Draw the character in the center of the image
    bbox = temp_draw.textbbox((font_size, font_size), char, font=font)
    temp_draw.text((font_size, font_size), char, font=font, fill=255)
    
    # Find the actual boundaries
    left, top, right, bottom = find_char_boundaries(temp_img)
    
    if left == right or top == bottom:
        # Handle space or empty characters
        width = font_size // 3
        height = font_size
        char_img = Image.new('L', (width, height), 0)
        return char_img, width, height
    
    # Extract the character with padding
    width = right - left + (padding * 2)
    height = bottom - top + (padding * 2)
    
    char_img = temp_img.crop((left - padding, top - padding, right + padding, bottom + padding))
    
    return char_img, width, height

def generate_bitmap_font(font_name, font_size):
    try:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        api_key = load_api_key(API_KEY_FILE)
        characters = load_characters(CHAR_FILE)
        
        font_file, font_name, font_style = download_google_font(font_name, api_key)
        font_id = f"{font_name.replace(' ', '')}_{font_style}"

        with Progress(console=console) as progress:
            task = progress.add_task(f"Generating bitmap fonts", total=len(SIZES))
            
            for size in SIZES:
                progress.update(task, description=f"Processing {size}x{size} resolution")
                dir_name = os.path.join(OUTPUT_DIR, f"resources-{size}x{size}")
                os.makedirs(dir_name, exist_ok=True)
                
                scale_factor = size / BASE_RESOLUTION
                scaled_font_size = int(font_size * scale_factor)
                
                font = ImageFont.truetype(font_file, scaled_font_size)
                char_data = {}
                row_data = []
                rows = []
                current_row_width = 0
                max_width = 0
                
                # First pass: Generate all character images and collect metrics
                for char in characters:
                    char_img, width, height = render_character(char, font)
                    char_data[char] = {
                        "charcode": ord(char),
                        "width": width,
                        "height": height,
                        "image": char_img
                    }
                    
                    if current_row_width + width > MAX_ROW_WIDTH:
                        rows.append(row_data)
                        max_width = max(max_width, current_row_width)
                        row_data = []
                        current_row_width = 0
                    
                    row_data.append(char)
                    current_row_width += width

                if row_data:
                    rows.append(row_data)
                    max_width = max(max_width, current_row_width)
                
                # Calculate total height
                total_height = sum(
                    max(char_data[char]["height"] for char in row)
                    for row in rows
                )
                
                # Create final image
                final_img = Image.new("L", (max_width, total_height), 0)
                y_offset = 0
                
                # Second pass: Compose the final image
                for row in rows:
                    x_offset = 0
                    row_height = max(char_data[char]["height"] for char in row)
                    
                    for char in row:
                        data = char_data[char]
                        final_img.paste(data["image"], (x_offset, y_offset))
                        x_offset += data["width"]
                    y_offset += row_height
                
                # Save the PNG
                png_path = os.path.join(dir_name, f"{font_id}.png")
                final_img.save(png_path)
                
                # Generate FNT file
                fnt_path = os.path.join(dir_name, f"{font_id}.fnt")
                with open(fnt_path, "w") as fnt_file:
                    fnt_file.write("info face=\"{}\" size={} bold={} italic={} charset=\"\" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0 outline=0\n".format(
                        font_name,
                        scaled_font_size,
                        1 if "bold" in font_style else 0,
                        1 if "italic" in font_style else 0
                    ))
                    fnt_file.write(f"common lineHeight={scaled_font_size} base={scaled_font_size} scaleW={max_width} scaleH={total_height} pages=1 packed=0\n")
                    fnt_file.write(f"page id=0 file=\"{font_id}.png\"\n")
                    fnt_file.write(f"chars count={len(char_data)}\n")
                    
                    # Write character information
                    y_offset = 0
                    for row in rows:
                        x_offset = 0
                        row_height = max(char_data[char]["height"] for char in row)
                        
                        for char in row:
                            data = char_data[char]
                            fnt_file.write("char id={} x={} y={} width={} height={} xoffset=0 yoffset=0 xadvance={} page=0 chnl=15\n".format(
                                data["charcode"],
                                x_offset,
                                y_offset,
                                data["width"],
                                data["height"],
                                data["width"]
                            ))
                            x_offset += data["width"]
                        y_offset += row_height
                
                # Generate XML file
                xml_path = os.path.join(dir_name, "fonts.xml")
                fonts = ET.Element("fonts")
                font_elem = ET.SubElement(fonts, "font")
                font_elem.set("id", font_id)
                font_elem.set("antialias", "true")
                font_elem.set("filename", f"{font_id}.fnt")
                
                tree = ET.ElementTree(fonts)
                tree.write(xml_path)
                
                progress.advance(task)
            
            console.print(f"[green]Successfully generated bitmap fonts in {OUTPUT_DIR}[/green]")

    except Exception as e:
        console.print(Panel.fit(
            f"[red]Error generating bitmap font: {str(e)}[/red]",
            title="Generation Error"
        ))
        sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download Google Font and generate bitmap font assets.")
    parser.add_argument("font_name", type=str, help="Name of the Google Font to download and use.")
    parser.add_argument("font_size", type=int, help="Font size to use for the default bitmap size.")
    
    try:
        args = parser.parse_args()
        console.print(Panel.fit(
            f"Starting bitmap font generation for:\n"
            f"Font: [cyan]{args.font_name}[/cyan]\n"
            f"Size: [cyan]{args.font_size}[/cyan]",
            title="Bitmap Font Generator"
        ))
        
        generate_bitmap_font(args.font_name, args.font_size)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(Panel.fit(
            f"[red]Unexpected error: {str(e)}[/red]",
            title="Error"
        ))
        sys.exit(1)

if __name__ == "__main__":
    main()