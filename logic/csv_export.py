import io
import csv
import codecs

def generate_csv(songs):
    """
    Generates a CSV file from a list of song strings.
    Each song string is expected to be in "Title - Artist" format or similar.
    Returns: BytesIO object containing the CSV file.
    """
    # Create an in-memory byte stream
    output = io.BytesIO()
    
    # Write BOM for Excel compatibility with UTF-8
    output.write(codecs.BOM_UTF8)
    
    # Wrap with TextIOWrapper to write strings
    wrapper = io.TextIOWrapper(output, encoding='utf-8', write_through=True)
    
    writer = csv.writer(wrapper)
    
    # Header
    writer.writerow(["Song Name", "Artist", "Original Text"])
    
    for song_str in songs:
        parts = song_str.split(" - ")
        if len(parts) >= 2:
            p1 = parts[0]
            p2 = " - ".join(parts[1:])
            writer.writerow([p1, p2, song_str])
        else:
            writer.writerow([song_str, "", song_str])
            
    # Detach wrapper so we don't close the BytesIO
    wrapper.detach()
    
    output.seek(0)
    return output
