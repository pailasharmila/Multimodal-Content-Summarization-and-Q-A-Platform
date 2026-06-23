# preprocessor.py
import re

def preprocess_transcript(raw_text: str) -> str:
    """
    Cleans a raw transcript text by removing timestamps,
    bracketed artifacts, and de-duplicating lines.
    
    This will clean text from both YouTube captions (Sample 1)
    and raw ASR (Sample 2).
    """
    
    # 1. Remove all timestamps and VTT-style tags (e.g., <00:00:00.000> or <c>)
    text = re.sub(r"<.*?>", "", raw_text)
    
    # 2. Remove all bracketed artifacts (e.g., [Music] or [Laughter])
    text = re.sub(r"\[.*?\]", "", text)
    
    # 3. Handle duplicate lines from caption formats and empty lines
    cleaned_lines = []
    seen = set()
    
    for line in text.splitlines():
        # Get rid of leading/trailing whitespace
        cleaned_line = line.strip()
        
        # If the line has content and we haven't seen it before, add it.
        # This handles both empty lines and the duplicate lines
        # found in your first sample.
        if cleaned_line and cleaned_line not in seen:
            cleaned_lines.append(cleaned_line)
            seen.add(cleaned_line)
    
    # 4. Join back into a single block of text
    print("--- Preprocessing Complete ---")
    ans= "\n".join(cleaned_lines)
    return ans

# --- ADDED TEST BLOCK ---
if __name__ == "__main__":
    
    print("--- TESTING SAMPLE 1 (YouTube Captions) ---")
    sample_text_1 = """
    [Music]
    hello
    welcome<00:00:31.039><c> to</c><00:00:31.199><c> the</c><00:00:31.359><c> course</c>
    welcome to the course
    on<00:00:32.480><c> design</c><00:00:32.960><c> and</c><00:00:33.120><c> implementation</c><00:00:33.760><c> of</c><00:00:34.079><c> human</c>
    on design and implementation of human
    computer<00:00:34.880><c> interfaces</c>
    computer interfaces
    let<00:00:37.040><c> us</c><00:00:37.200><c> know</c>
    let us know
    in<00:00:38.559><c> this</c><00:00:38.800><c> course</c><00:00:39.120><c> what</c><00:00:39.360><c> we</c><00:00:39.520><c> are</c><00:00:39.600><c> going</c><00:00:39.840><c> to</c>
    in this course what we are going to
    learn
    [Music]
    """
    cleaned_text_1 = preprocess_transcript(sample_text_1)
    print(cleaned_text_1)

    print("\n" + "="*40 + "\n")

    print("--- TESTING SAMPLE 2 (Raw ASR) ---")
    sample_text_2 = """
     I wanna be a fault container I will never run If you like your coffee, I'll Let me be a coffee, ma'am You call the shots, babe I just wanna be your Secrets I have held in my heart I've had too high than I thought Maybe I just wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be your own Let me be your lucky meter And I'll never run out Let me be the portable heater And charge it cold out I wanna be a setting lotion Won't you hear a deep deflection? At least as deep as the Pacific Ocean I wanna be your Secrets I have held in my heart I've had too high than I thought Maybe I just wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours Won't be alone Won't be alone When the sun soul will roupa out He tried 13 years of concern You have simple And before You're only one being left to smile with You're only one being left to smile with You're only one being You're only one being left to smile with You're only one being left to smile with
    """
    cleaned_text_2 = preprocess_transcript(sample_text_2)
    print(cleaned_text_2)
    