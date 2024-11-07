# Garmin Bitmap Font Generator

A Python utility that generates bitmap fonts compatible with Garmin devices using Google Fonts. This tool analyzes character pixel data to create optimally-spaced bitmap fonts with proper character boundaries.

## Features

- Downloads fonts from Google Fonts API
- Generates bitmap fonts in multiple resolutions (454x454, 416x416, 390x390, 360x360)
- Supports different font styles (regular, bold, italic, bolditalic)
- Optimized character spacing using pixel analysis
- Generates all required files for Garmin font implementation
- Interactive font style selection
- Progress visualization
- Error handling and user feedback

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  ```bash
  pip install Pillow requests rich numpy
  ```

## Project Structure

```
project/
├── config.py               # Configuration constants
├── utils.py               # Utility functions
├── font_manager.py        # Font download and selection
├── bitmap_generator.py    # Main bitmap generation logic
├── generate.py           # Entry point
├── requirements.txt      # Python dependencies
├── apikey.txt           # Google Fonts API key
└── char.txt             # Characters to include in the font
```

## Setup

1. Create a `char.txt` file with the characters you want to include:
   ```text
   0123456789:ABCDEFGHIJKLM.,-
   ```

2. Get a Google Fonts API key:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Fonts API
   - Go to "APIs & Services" > "Credentials"
   - Create an API key
   - Save the key in `apikey.txt`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic command:
```bash
python generate.py "Font Name" font_size
```

Examples:
```bash
# Generate Roboto font with size 71
python generate.py "Roboto" 71

# Generate Open Sans font with size 53
python generate.py "Open Sans" 53
```

## Output Structure

The tool generates the following files for each resolution:
```
output/
├── resources-454x454/
│   ├── FontName_style.png    # Bitmap font image
│   ├── FontName_style.fnt    # Font metrics file
│   └── fonts.xml            # Garmin font configuration
├── resources-416x416/
│   └── ...
├── resources-390x390/
│   └── ...
└── resources-360x360/
    └── ...
```

## File Descriptions

1. `.png` file:
   - Black background with white characters
   - Optimally spaced characters
   - No extra padding or margins

2. `.fnt` file:
   - Contains font metrics and character mapping
   - Includes character positions and dimensions
   - Specifies font properties and settings

3. `fonts.xml`:
   - Garmin-specific font configuration
   - References the font files
   - Sets font properties like antialiasing

## Implementation in Garmin Projects

1. Copy the generated resources to your Garmin project's resources directory
2. Use the appropriate resolution folder for your target device
3. Reference the font in your layouts:
   ```xml
   <font id="CustomFont" filename="FontName_style.fnt" />
   ```

## Error Handling

The tool includes comprehensive error handling for:
- Missing or invalid API key
- Network connectivity issues
- Font download failures
- Invalid font names or styles
- Character rendering issues
- File system operations

## Best Practices

1. Use appropriate font sizes for your target devices
2. Include only necessary characters to minimize file size
3. Test the generated fonts on target devices
4. Keep the generated files in your version control
5. Document font usage in your Garmin project

## Limitations

1. Maximum texture size depends on target device specifications
2. Characters must be defined in advance via char.txt
3. Some fonts might not support all styles

## Contributing

Feel free to open issues or submit pull requests for:
- Bug fixes
- Feature improvements
- Documentation updates
- New features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Fonts API for providing the font library
- PIL (Python Imaging Library) for image processing
- Rich library for beautiful console output