import io
import re
from openpyxl import Workbook

def generate_excel(songs):
    """
    Generates an Excel file from a list of song strings.
    Each song string is expected to be in "Title - Artist" format or similar.
    Returns: BytesIO object containing the Excel file.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Song List"
    
    # Header
    ws.append(["Song Name", "Artist", "Original Text"])
    
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    
    def sanitize(text):
        if not text: 
            return ""
        return ILLEGAL_CHARACTERS_RE.sub("", str(text))
    
    for song_str in songs:
        clean_song_str = sanitize(song_str)
        parts = clean_song_str.split(" - ")
        if len(parts) >= 2:
            p1 = parts[0]
            p2 = " - ".join(parts[1:])
            ws.append([p1, p2, clean_song_str])
        else:
            ws.append([clean_song_str, "", clean_song_str])
            
    # Auto-adjust column width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
