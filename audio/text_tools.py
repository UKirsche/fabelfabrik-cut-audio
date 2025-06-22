import os

def split_text_into_chunks(text: str, max_length: int = 2500) -> list[str]:
    """
    Teilt den Text in Abschnitte von maximal max_length Zeichen.
    Jeder Abschnitt endet an einem Punkt (.)
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_length, text_length)
        last_period = text.rfind('.', start, end)

        if last_period == -1 or last_period <= start:
            last_period = end

        chunk = text[start:last_period + 1].strip()
        chunks.append(chunk)

        start = last_period + 1
        while start < text_length and text[start].isspace():
            start += 1

    return chunks

def save_chunks_to_files(text: str, output_dir: str, base_name: str = "story"):
    """
    Speichert den Originaltext und die Chunks als separate .txt-Dateien.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Speichere den kompletten Text
    story_path = os.path.join(output_dir, f"{base_name}.txt")
    with open(story_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Original gespeichert: {story_path}")

    # Splitten & speichern
    chunks = split_text_into_chunks(text)
    for idx, chunk in enumerate(chunks, start=1):
        chunk_filename = f"{base_name}{idx}.txt"
        chunk_path = os.path.join(output_dir, chunk_filename)
        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(chunk)
        print(f"Chunk gespeichert: {chunk_path}")
