import re
import pandas as pd


# Function 1: Remove useless lines from PDF text
def remove_bad_lines(text):
    text = str(text)

    lines = text.splitlines()

    correct_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if line == "":
            continue

        # Skip lines with only page numbers
        if re.fullmatch(r"\d+", line):
            continue

        # Skip page footer/header like Page 1, page 2
        if re.fullmatch(r"page\s*\d+", line.lower()):
            continue

        # Skip very short lines
        if len(line) < 3:
            continue

        correct_lines.append(line)

    return " ".join(correct_lines)


# Function 2: Clean text
def clean_text(text):
    text = remove_bad_lines(text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", " ", text)

    # Fix words broken by hyphen(health- care -> healthcare)

    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

    # Keep only useful English characters, numbers, and medical symbols
    text = re.sub(r"[^a-zA-Z0-9\s.,:/()%\-]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# Function 3: Check whether a chunk is useful
def is_chunk_useful(text):
    words = text.split()

    # Skip very short chunks
    if len(words) < 40:
        return False

    # Skip chunks with too many numbers/symbols and very few letters
    total_chars = len(text)

    if total_chars == 0:
        return False

    letter_count = 0

    for char in text:
        if char.isalpha():
            letter_count = letter_count + 1

    letter_ratio = letter_count / total_chars

    if letter_ratio < 0.35:
        return False

    return True


# Function 4: Split long text into small chunks
def split_into_chunks(text, chunk_size=120):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)

        if is_chunk_useful(chunk_text):
            chunks.append(chunk_text)

    return chunks


# Function 5: Clean and organize dataset
def clean_dataset():
    raw_file = "data/raw_srilanka_health_text.csv"
    output_file = "data/clean_srilanka_health_text.csv"

    df = pd.read_csv(raw_file)

    print("Raw records:", len(df))

    all_rows = []

    for index, row in df.iterrows():
        source_name = row.get("source_name", "")
        source_page = row.get("source_page", "")
        document_title = row.get("document_title", "")
        pdf_url = row.get("pdf_url", "")
        text = row.get("text", "")

        cleaned = clean_text(text)

        chunks = split_into_chunks(cleaned, chunk_size=120)

        for chunk_id, chunk_text in enumerate(chunks, start=1):
            all_rows.append({
                "source_name": source_name,
                "source_page": source_page,
                "document_title": document_title,
                "pdf_url": pdf_url,
                "chunk_id": chunk_id,
                "cleaned_text": chunk_text,
                "word_count": len(chunk_text.split()),
                "char_count": len(chunk_text)
            })

    clean_df = pd.DataFrame(all_rows)

    if clean_df.empty:
        print("No cleaned data created.")
        return

    # Remove duplicate text chunks
    clean_df.drop_duplicates(subset=["cleaned_text"], inplace=True)

    # Save cleaned dataset
    clean_df.to_csv(output_file, index=False, encoding="utf-8")

    print("Cleaned records:", len(clean_df))
    print("Saved file:", output_file)

    print("Sample cleaned rows:")
    print(clean_df.head())


clean_dataset()