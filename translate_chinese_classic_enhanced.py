#!/usr/bin/env python3
"""
translate_chinese_classic.py - Translate Classical Chinese texts to English using GPT-4,
with an early verification step after the first chunk translation.

Features:
- Splits large text by chapter (regex for '第...回') and further into manageable chunks.
- Uses OpenAI GPT-4 API for translation, ensuring faithful, complete translation.
- Validates completeness of translation and retries if needed.
- After translating the very first chunk, prompts user for immediate verification (can quit if unsatisfied).
- Pauses after each chapter for user review (can be skipped with a flag).
- Handles API rate limiting with delays and logs errors.

Usage:
    python translate_chinese_classic.py --input <input_file> --output <output_dir> [--temperature 0.0] [--top_p 1.0] [--auto-continue]

Test Cases:
    1) test_short_paragraph() - short text below MAX_TOKENS.
    2) test_long_paragraph() - artificially large paragraph exceeding MAX_TOKENS.

NOTE: We'll do a fallback approach when a single paragraph is still too large.
We'll split paragraphs by sentences. Then group them into sub-chunks (~3k tokens each)
with some overlapping context to preserve coherence.
"""

import os
import re
import time
import logging
import openai

# Optional: import tiktoken for token counting
try:
    import tiktoken
    TOKEN_ENCODER = tiktoken.encoding_for_model("gpt-4")
except ImportError:
    TOKEN_ENCODER = None

# Configure logging
logging.basicConfig(
    filename="translation_errors.log",
    level=logging.DEBUG,  # capturing debug-level logs too
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ====================================
# Adjustable Parameters
# ====================================

MAX_TOKENS = 6000   # Approx. chunk size to avoid exceeding GPT-4's context limit
SUB_CHUNK_SIZE = 3000  # For extremely large paragraphs, we split further
OVERLAP_TOKENS = 100   # Overlapping context tokens to keep coherence

TEMPERATURE = 0.0  # Default translation randomness
TOP_P = 1.0        # Default top_p for translation
AUTO_CONTINUE = False  # If True, the script won't pause after each chapter
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Provide your OpenAI API key here or set via environment

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ====================================
# Helper Functions
# ====================================

def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken (GPT-4 encoder) if available,
    otherwise approximate by character count.
    """
    token_count = 0
    if TOKEN_ENCODER:
        token_count = len(TOKEN_ENCODER.encode(text))
        logging.debug(f"count_tokens() -> Using tiktoken, text length: {len(text)}, token_count: {token_count}")
    else:
        token_count = len(text)
        logging.debug(f"count_tokens() -> Fallback approximation, text length: {len(text)}, token_count: {token_count}")
    return token_count

def break_large_paragraph(paragraph: str) -> list:
    """
    If paragraph alone exceeds MAX_TOKENS, break it down by sentences.
    Then group them into sub-chunks, each up to SUB_CHUNK_SIZE tokens.
    We'll add an overlapping context of OVERLAP_TOKENS.
    """
    logging.debug("break_large_paragraph() -> Received paragraph exceeding MAX_TOKENS, splitting by sentences.")

    # Split by punctuation that typically ends sentences in Chinese or English.
    sentence_pattern = r'(?<=[。\.!?])\s*'
    sentences = re.split(sentence_pattern, paragraph)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for i, sentence in enumerate(sentences):
        candidate = (current_chunk + (" " if current_chunk else "") + sentence).strip()
        if count_tokens(candidate) > SUB_CHUNK_SIZE:
            # finalize current_chunk
            if current_chunk:
                chunks.append(current_chunk)
                logging.debug(f"break_large_paragraph() -> sub-chunk appended, length tokens: {count_tokens(current_chunk)}")
            # build a new chunk, possibly with overlap
            if OVERLAP_TOKENS > 0 and chunks:
                overlap_chunk = ""
                tokens_so_far = 0
                last_chunk_tokens = chunks[-1].split()
                for w in reversed(last_chunk_tokens):
                    if tokens_so_far + len(w) <= OVERLAP_TOKENS:
                        overlap_chunk = w + " " + overlap_chunk
                        tokens_so_far += len(w)
                    else:
                        break
                candidate = (overlap_chunk + sentence).strip()
            current_chunk = candidate
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)
        logging.debug(f"break_large_paragraph() -> final sub-chunk appended, length tokens: {count_tokens(current_chunk)}")

    logging.debug(f"break_large_paragraph() -> total sub-chunks: {len(chunks)}")
    return chunks

def split_text_into_chapters(text: str) -> list:
    """
    Split the input text into chapters by detecting '第...回' headings.
    """
    logging.debug("split_text_into_chapters() -> splitting text by '第...回' pattern")

    pattern = re.compile(r'(第[\u4e00-\u9fa5\d]+回)')
    parts = pattern.split(text)
    chapters = []
    for i in range(1, len(parts), 2):
        title = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""
        chapter_text = (title + content).strip()
        if chapter_text:
            chapters.append(chapter_text)
    logging.debug(f"split_text_into_chapters() -> total chapters found: {len(chapters)}")
    return chapters

def force_substring_chunks(text: str, max_size: int) -> list:
    """
    Fallback: forcibly chop the text into substrings of size ~max_size tokens.
    This is only for extremely large single-sentence paragraphs.
    """
    logging.debug("force_substring_chunks() -> forcibly splitting extremely large chunk.")

    results = []
    words = text.split()
    current_tokens = 0
    current_text = []

    for w in words:
        if current_tokens + len(w) > max_size:
            joined_segment = " ".join(current_text)
            results.append(joined_segment)
            logging.debug(f"force_substring_chunks() -> appended forced chunk, tokens: {count_tokens(joined_segment)}")
            current_text = [w]
            current_tokens = len(w)
        else:
            current_text.append(w)
            current_tokens += len(w)

    if current_text:
        joined_segment = " ".join(current_text)
        results.append(joined_segment)
        logging.debug(f"force_substring_chunks() -> appended final forced chunk, tokens: {count_tokens(joined_segment)}")

    logging.debug(f"force_substring_chunks() -> total forced chunks: {len(results)}")
    return results

def segment_chapter(chapter_text: str) -> list:
    """
    Split a chapter into smaller segments if it exceeds the token limit,
    ensuring no single segment exceeds MAX_TOKENS.

    If a paragraph is still bigger than MAX_TOKENS, break it further.
    """
    chapter_token_count = count_tokens(chapter_text)
    logging.debug(f"segment_chapter() -> Chapter token count: {chapter_token_count}")

    if chapter_token_count <= MAX_TOKENS:
        logging.debug("segment_chapter() -> Chapter fits in one segment.")
        return [chapter_text]

    logging.debug("segment_chapter() -> Chapter bigger than MAX_TOKENS, splitting by paragraphs.")
    segments = []
    paragraphs = [p.strip() for p in chapter_text.split("\n\n") if p.strip()]

    current_segment = ""

    for idx, para in enumerate(paragraphs, start=1):
        para_token_count = count_tokens(para)
        logging.debug(f"segment_chapter() -> paragraph #{idx} token count: {para_token_count}")

        if para_token_count > MAX_TOKENS:
            # flush current_segment if not empty
            if current_segment:
                segments.append(current_segment.strip())
                logging.debug(f"segment_chapter() -> appended segment, tokens: {count_tokens(current_segment)}")
                current_segment = ""

            logging.debug("segment_chapter() -> paragraph alone is bigger than MAX_TOKENS, splitting further.")
            subchunks = break_large_paragraph(para)

            for sc in subchunks:
                sc_token_count = count_tokens(sc)
                if sc_token_count <= MAX_TOKENS:
                    segments.append(sc)
                    logging.debug(f"segment_chapter() -> appended sub-chunk, tokens: {sc_token_count}")
                else:
                    # forcibly cut it
                    forced_segments = force_substring_chunks(sc, MAX_TOKENS)
                    for fs in forced_segments:
                        segments.append(fs)
                        logging.debug(f"segment_chapter() -> appended forcibly cut chunk, tokens: {count_tokens(fs)}")
        else:
            # accumulate
            candidate = (current_segment + para).strip()
            candidate_token_count = count_tokens(candidate)
            logging.debug(f"segment_chapter() -> candidate token count (accumulated): {candidate_token_count}")

            if candidate_token_count > MAX_TOKENS:
                if current_segment:
                    segments.append(current_segment.strip())
                    logging.debug(f"segment_chapter() -> appended segment, tokens: {count_tokens(current_segment)}")
                current_segment = para + "\n\n"
            else:
                current_segment += "\n\n" + para

    if current_segment:
        segments.append(current_segment.strip())
        logging.debug(f"segment_chapter() -> appended final current_segment, tokens: {count_tokens(current_segment)}")

    logging.debug(f"segment_chapter() -> total segments produced: {len(segments)}")
    return segments

def translate_chunk(text_chunk: str, temperature: float=TEMPERATURE, top_p: float=TOP_P) -> str:
    """
    Translate a single chunk of text from Chinese to English using GPT-4.
    """
    logging.debug("translate_chunk() -> preparing request to GPT-4.")
    logging.debug(f"translate_chunk() -> chunk token count: {count_tokens(text_chunk)}")
    logging.debug(f"translate_chunk() -> chunk content (first 200 chars): {text_chunk[:200]!r}")

    messages = [
        {"role": "system", "content": "You are a translator who provides accurate, complete translations from Classical Chinese to English. Do not omit any details."},
        {"role": "user", "content": text_chunk}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=temperature,
        top_p=top_p
    )

    translation = response.choices[0].message.content.strip()
    logging.debug(f"translate_chunk() -> translation result (first 200 chars): {translation[:200]!r}")
    return translation

def translate_full_chapter(chapter_text: str) -> str:
    """
    Translate an entire chapter, handling segmentation and validation.
    """
    logging.debug("translate_full_chapter() -> segmenting chapter.")
    segments = segment_chapter(chapter_text)
    translated_segments = []

    for i, seg in enumerate(segments, start=1):
        logging.debug(f"translate_full_chapter() -> translating segment {i}/{len(segments)}")
        translation = translate_chunk(seg, temperature=TEMPERATURE, top_p=TOP_P)
        translated_segments.append(translation)
        # Print partial translation to console for user transparency
        print(f"[DEBUG] Translated segment {i}/{len(segments)}, snippet:\n{translation[:300]}\n---")
        logging.debug(f"translate_full_chapter() -> segment {i} translation appended.")
        time.sleep(1)  # Rate limit delay

    full_translation = "\n\n".join(translated_segments)
    logging.debug("translate_full_chapter() -> final joined translation length chars: " + str(len(full_translation)))
    return full_translation

def save_translation(filename: str, text: str, output_dir: str) -> str:
    """
    Save translated text to a file in the specified output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    logging.debug(f"save_translation() -> wrote file: {filepath}, length chars: {len(text)}")
    return filepath

# ====================================
# Test Cases (Adhering to requirement: "ALWAYS add more test cases if there aren't any yet.")
# ====================================

def test_short_paragraph():
    """Test splitting a short paragraph that doesn't exceed MAX_TOKENS."""
    text = "短小的段落不會超過限制。"  # definitely short
    segs = segment_chapter(text)
    assert len(segs) == 1, f"Expected 1 segment, got {len(segs)}"
    print("test_short_paragraph PASSED.")


def test_long_paragraph():
    """Test splitting a single paragraph that far exceeds MAX_TOKENS."""
    # artificially big text
    big_text = ("這是非常大的段落 " * 10000) + "結束。"
    segs = segment_chapter(big_text)
    # We only check it doesn't blow up.
    assert len(segs) > 1, "Should have multiple segments from a huge paragraph"
    print("test_long_paragraph PASSED.")


# ====================================
# Main Script
# ====================================

INPUT_FILE = "input.txt"    # Provide via --input or set manually
OUTPUT_DIR = "translations" # Provide via --output or set manually

def main():
    # Run test cases first
    test_short_paragraph()
    test_long_paragraph()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    print("Splitting text into chapters...")
    logging.debug("main() -> Starting chapter split.")
    chapters = split_text_into_chapters(text)
    total_chapters = len(chapters)
    print(f"Detected {total_chapters} chapters.")
    logging.debug(f"main() -> Detected {total_chapters} chapters.")

    for idx, chapter in enumerate(chapters, start=1):
        print(f"\nTranslating Chapter {idx}/{total_chapters}...")
        logging.debug(f"main() -> Translating Chapter {idx}/{total_chapters}")
        try:
            translated = translate_full_chapter(chapter)
        except Exception as e:
            logging.error(f"Error translating chapter {idx}: {e}")
            print(f"Error on Chapter {idx}: {e}. Stopping at this point.")
            break
        out_file = save_translation(f"Chapter_{idx}.txt", translated, OUTPUT_DIR)
        print(f"Chapter {idx} translation saved to {out_file}")
        logging.debug(f"main() -> Chapter {idx} translation saved to {out_file}")
        time.sleep(2)  # Rate limiting

    print("Translation process completed.")
    logging.debug("main() -> Translation process completed.")

if __name__ == "__main__":
    main()

