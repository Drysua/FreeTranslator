
# Free Translator App

The application translates first 100000 characters of file via [DeepL Official Translator website](https://www.deepl.com/en/translator) using your free everyday limit, then switches to GoogleTranslate API and proceed the rest.

## Features

- Supports multiple translation sources (Deepl, Google Translate).
- Dynamically adjusts separators to ensure seamless chunk processing.
- GUI-based interface for ease of use.
- Customizable settings for translating files or text chunks.
- Bundled as a standalone executable using `cx_Freeze` for portability.
  
## Input/Output Formats
App translate file string by string of given format
### Input file (utf-8)

```  
string_id|source_lang_text||
```
### Output file (utf-8)

```  
string_id|source_lang_text|target_lang_text|
```

## Requirements

- Python 3.8+
- `selenium` library for web automation.
- WebDriver Manager to manage browser drivers automatically. 
- `deep_translate` library for GoogleTranslate api calls
- `cx_Freeze` for building into exe

## Installation

### Clone the Repository
```bash
git clone https://github.com/yourusername/free-translator.git
cd free-translator
```

### Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Build the Executable (Optional)
To build the app as an executable:
1. Make sure `cx_Freeze` is installed:
   ```bash
   pip install cx_Freeze
   ```

2. Run the `setup.py` script:
   ```bash
   python setup.py build
   ```

3. The executable will be located in the `build` folder.

## Usage

### Running the App
If you have the executable:
1. Navigate to the `build` directory.
2. Run the app:
   ```bash
   ./gui.exe
   ```

If you are running the script directly:
```bash
python gui.py
```

### Translating Text Files
1. Launch the app.
2. Load a text file to translate.
3. Select the desired source and target language.
4. Choose or configure the chunk separator.
5. Click "Translate" and save the output.

### Separator Customization
The app dynamically adjusts separators to ensure unique chunk division. You can:
- Define custom separators in the GUI.
- Use the **SeparatorManager** to rotate through predefined separators.

## Icon Usage
This app includes a custom icon (`app_icon.ico`) that appears on the executable and the GUI.

## Troubleshooting

### Common Issues
- **Missing DLLs**: Ensure you have all dependencies installed, and include missing files in `setup.py`.
- **WebDriver Not Found**: The app uses `webdriver-manager` to download and manage the required WebDriver for Selenium. Ensure your internet connection is stable.

### Debugging
Run the app in a terminal to view error messages:
```bash
python gui.py
```
