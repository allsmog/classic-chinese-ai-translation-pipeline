# Classical Chinese Translator

A tool for translating Classical Chinese texts into English using GPT-4. This project is designed to handle long classical texts like novels or philosophical works, providing high-quality translations with minimal human intervention.

## Features

- **Smart Text Segmentation**: Automatically splits texts into chapters and manageable chunks
- **Quality Control**: Validates translations and retries incomplete segments
- **Early Verification**: Allows checking the first translated chunk before committing to the full process
- **User Review**: Optionally pauses after each chapter for review
- **Error Handling**: Robust error logging and rate limiting for API calls

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/classical-chinese-translator.git
   cd classical-chinese-translator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API key
   ```

## Usage

### Basic Usage

```bash
python translate_chinese_classic.py --input your_text.txt --output translations
```

For better handling of complex texts with large paragraphs, use the enhanced version:

```bash
python translate_chinese_classic_enhanced.py --input your_text.txt --output translations
```

### Advanced Options

```bash
python translate_chinese_classic.py --input your_text.txt --output translations --temperature 0.1 --top_p 0.9 --auto-continue
```

- `--input`: Path to the input text file (required)
- `--output`: Directory to save translations (required)
- `--temperature`: Controls randomness in the translation (default: 0.0)
- `--top_p`: Controls diversity via nucleus sampling (default: 1.0)
- `--auto-continue`: Skip manual review between chapters

### Example

The repository includes a sample of "Dream of the Red Chamber" (红楼梦) in the `examples` directory:

```bash
python translate_chinese_classic.py --input examples/dream_of_red_chamber_sample.txt --output sample_translations
```

## Structure

- `translate_chinese_classic.py`: Main script with standard text processing and translation functionality
- `translate_chinese_classic_enhanced.py`: Enhanced version with improved chunking and robust error handling for complex texts (recommended for most users)
- `requirements.txt`: Project dependencies
- `docs/`: Documentation and guides
- `examples/`: Sample texts and translations

## How It Works

1. **Text Splitting**: The script detects chapter boundaries using regex patterns (e.g., '第...回' for classical novels)
2. **Chunking**: Each chapter is divided into digestible segments for the API
3. **Translation**: Each segment is translated using GPT-4
4. **Validation**: The result is checked for completeness
5. **Combination**: Translated segments are joined and saved as chapter files

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4
- Contributors to tiktoken for efficient token counting

## Disclaimer

This tool is designed for educational and research purposes. Please respect copyright laws when translating protected works.
