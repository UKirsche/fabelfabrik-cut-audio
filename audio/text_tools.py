import os
from typing import List, Iterator
from dataclasses import dataclass

@dataclass
class ChunkConfig:
    """Konfiguration für das Text-Chunking"""
    max_length: int = 2500
    sentence_end_char: str = '.'
    min_chunk_length: int = 100

class TextChunker:
    """Verantwortlich für das Aufteilen von Text in Chunks"""
    
    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()
    
    def split_text(self, text: str) -> List[str]:
        """Teilt Text in sinnvolle Chunks auf"""
        if not text.strip():
            return []
        
        return list(self._generate_chunks(text.strip()))
    
    def _generate_chunks(self, text: str) -> Iterator[str]:
        """Generator für Chunks - memory-efficient"""
        text_length = len(text)
        position = 0
        
        while position < text_length:
            chunk = self._extract_next_chunk(text, position)
            if chunk.content:
                yield chunk.content
            position = chunk.next_position
    
    def _extract_next_chunk(self, text: str, start_pos: int) -> 'ChunkResult':
        """Extrahiert den nächsten Chunk ab der gegebenen Position"""
        text_length = len(text)
        max_end = min(start_pos + self.config.max_length, text_length)
        
        # Wenn wir das Ende erreicht haben
        if max_end >= text_length:
            content = text[start_pos:].strip()
            return ChunkResult(content, text_length)
        
        # Suche optimalen Schnitt-Punkt
        cut_position = self._find_optimal_cut_position(text, start_pos, max_end)
        content = text[start_pos:cut_position + 1].strip()
        next_pos = self._skip_whitespace(text, cut_position + 1)
        
        return ChunkResult(content, next_pos)
    
    def _find_optimal_cut_position(self, text: str, start: int, max_end: int) -> int:
        """Findet die beste Position zum Schneiden des Texts"""
        sentence_end = text.rfind(self.config.sentence_end_char, start, max_end)
        
        # Wenn Satz-Ende gefunden und sinnvoll positioniert
        if sentence_end != -1 and sentence_end > start:
            return sentence_end
        
        # Fallback: am Wortende schneiden
        return self._find_word_boundary(text, start, max_end)
    
    def _find_word_boundary(self, text: str, start: int, max_end: int) -> int:
        """Findet Wortgrenze für sauberen Schnitt"""
        # Rückwärts nach Leerzeichen suchen
        for pos in range(max_end - 1, start, -1):
            if text[pos].isspace():
                return pos - 1
        
        # Fallback: harter Schnitt
        return max_end - 1
    
    def _skip_whitespace(self, text: str, position: int) -> int:
        """Überspringt Leerzeichen ab der gegebenen Position"""
        while position < len(text) and text[position].isspace():
            position += 1
        return position

@dataclass
class ChunkResult:
    """Ergebnis einer Chunk-Extraktion"""
    content: str
    next_position: int

class FileManager:
    """Verantwortlich für Datei-Operationen"""
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """Stellt sicher, dass das Verzeichnis existiert"""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def write_text_file(filepath: str, content: str) -> None:
        """Schreibt Text in eine Datei"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

class TextProcessor:
    """Hauptklasse für Text-Verarbeitung"""
    
    def __init__(self, chunker: TextChunker = None, file_manager: FileManager = None):
        self.chunker = chunker or TextChunker()
        self.file_manager = file_manager or FileManager()
    
    def process_and_save(self, text: str, output_dir: str, base_name: str = "story", 
                        chunk_length: int = 2500) -> None:
        """Verarbeitet Text und speichert Original + Chunks"""
        # Konfiguration anpassen
        self.chunker.config.max_length = max(chunk_length, self.chunker.config.min_chunk_length)
        
        # Verzeichnis vorbereiten
        self.file_manager.ensure_directory(output_dir)
        
        # Original speichern
        self._save_original(text, output_dir, base_name)
        
        # Chunks erstellen und speichern
        self._save_chunks(text, output_dir, base_name)
    
    def _save_original(self, text: str, output_dir: str, base_name: str) -> None:
        """Speichert den Original-Text"""
        original_path = os.path.join(output_dir, f"{base_name}.txt")
        self.file_manager.write_text_file(original_path, text)
        print(f"Original gespeichert: {original_path}")
    
    def _save_chunks(self, text: str, output_dir: str, base_name: str) -> None:
        """Erstellt und speichert alle Chunks"""
        chunks = self.chunker.split_text(text)
        
        for idx, chunk in enumerate(chunks, start=1):
            chunk_filename = f"{base_name}{idx}.txt"
            chunk_path = os.path.join(output_dir, chunk_filename)
            self.file_manager.write_text_file(chunk_path, chunk)
            print(f"Chunk {idx} gespeichert: {chunk_path}")

# Convenience-Funktionen für Backward-Compatibility
def split_text_into_chunks(text: str, max_length: int = 2500) -> List[str]:
    """Legacy-Funktion für Rückwärtskompatibilität"""
    config = ChunkConfig(max_length=max_length)
    chunker = TextChunker(config)
    return chunker.split_text(text)

def save_chunks_to_files(text: str, output_dir: str, base_name: str = "story", max_length: int = 2500):
    """Legacy-Funktion für Rückwärtskompatibilität"""
    processor = TextProcessor()
    processor.process_and_save(text, output_dir, base_name, max_length)