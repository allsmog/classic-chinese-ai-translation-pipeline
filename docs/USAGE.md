# Usage Guide

This guide provides detailed instructions on how to use the Classical Chinese Translator.

## Basic Translation

The most basic usage is to translate a single file:

```bash
python translate_chinese_classic.py --input your_text.txt --output translations
```

This will:
1. Read the Chinese text from `your_text.txt`
2. Split it into chapters (if applicable)
3. Translate each chapter
4. Save the translated files to the `translations` directory

## Command Line Arguments

The script supports the following command line arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--input` | Path to the input text file | (Required) |
| `--output` | Directory to save translations | (Required) |
| `--temperature` | Temperature for the translation (0.0-1.0) | 0.0 |
| `--top_p` | Top-p for nucleus sampling (0.0-1.0) | 1.0 |
| `--auto-continue` | Skip manual review between chapters | False |

## Translation Quality

The quality of the translation can be adjusted using the `--temperature` and `--top_p` parameters:

- **Lower temperature** (0.0-0.3): More consistent, conservative translations
- **Higher temperature** (0.4-0.8): More creative translations
- **Top-p**: Controls diversity via nucleus sampling

For most classical texts, we recommend keeping temperature low (0.0-0.2) for accuracy.

## Handling Large Texts

For very large texts, you may want to:

1. Split the text into separate files (e.g., by chapter or section)
2. Process each file separately
3. Use `translate_chinese_classic_extended.py` which has better handling for extremely large paragraphs

Example for large texts:

```bash
python translate_chinese_classic_extended.py --input chapter1.txt --output translations
```

## Workflow Recommendations

For best results with large classical works:

1. **Test on a small section first** to verify quality
2. Use the early verification feature to check translation quality
3. For works with unusual vocabulary or style, consider customizing the system prompt in the script
4. Save translations frequently and keep backups

## API Usage and Costs

This tool uses the OpenAI API, which charges based on token usage. To estimate costs:

- Classical Chinese texts typically use fewer tokens than their English translations
- Each Chinese character is roughly 1-2 tokens
- The translation usually expands the text by 2-4x in terms of token count

Monitor your usage through the OpenAI dashboard to avoid unexpected charges.

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your OpenAI API key is correctly set in the `.env` file
   - Check that your API key hasn't expired or reached its usage limit

2. **Rate Limiting**
   - If you encounter rate limiting errors, the script will pause, but you may need to increase the delay between API calls

3. **Memory Issues**
   - For very large texts, you may encounter memory issues. Try using smaller chunks or the extended version of the script.

4. **Validation Failures**
   - The script validates translations by comparing sentence counts. This may sometimes fail for texts with unusual punctuation.

### Getting Help

If you encounter issues not covered here, please:

1. Check the logs in `translation_errors.log`
2. Open an issue on GitHub with detailed information about the problem
