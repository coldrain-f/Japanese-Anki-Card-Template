import os
import time
from aqt import mw
from aqt.utils import showInfo, getFile
from anki.notes import Note

# Global cache for frequency map
FREQUENCY_MAP = None

def get_config():
    return mw.addonManager.getConfig(__name__)

def load_frequency_map():
    global FREQUENCY_MAP
    if FREQUENCY_MAP is not None:
        return FREQUENCY_MAP
    
    # Path to JPDB.txt on Desktop (as user indicated)
    # We can also look in the addon folder or ask user to select.
    # Let's try Desktop first, then fallback to asking user.
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop, "JPDB.txt")
    
    if not os.path.exists(file_path):
        # Fallback: Look in addon directory
        addon_dir = os.path.dirname(__file__)
        file_path = os.path.join(addon_dir, "JPDB.txt")
        
    if not os.path.exists(file_path):
        # Fallback: Ask user
        key = getFile(mw, "Select JPDB.txt Frequency File", None, "Text Files (*.txt)")
        if not key:
            return None
        file_path = key

    freq_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    word = parts[0]
                    rank = parts[1]
                    # Handle potential duplicates or variations?
                    # Since it's a map, last one wins or first one?
                    # Usually file is sorted by rank?
                    # The sample shows "word \t rank".
                    if word not in freq_map:
                        freq_map[word] = rank
        FREQUENCY_MAP = freq_map
        return freq_map
    except Exception as e:
        showInfo(f"Error loading JPDB.txt: {str(e)}")
        return None

def is_sentence(text):
    if not text:
        return False
    if "。" in text or "、" in text:
        return True
    if len(text) > 15:
        return True
    return False

def get_frequency_local(text):
    freq_map = load_frequency_map()
    if not freq_map:
        return None, "File not loaded"
    
    if text in freq_map:
        return freq_map[text], None
        
    return None, "Not found in list"

def fill_frequency_for_selected_cards(browser):
    config = get_config()
    source_field = config.get('source_field', 'Expression')
    target_field = config.get('target_field', 'Frequency')
    overwrite = config.get('overwrite', False)
    ignore_sentences = config.get('ignore_sentences', True)

    # Ensure map is loaded before starting
    if not load_frequency_map():
        showInfo("Could not load JPDB.txt. Please ensure it is on your Desktop or selected.")
        return

    selected_nids = browser.selectedNotes()

    if not selected_nids:
        showInfo("No cards selected.")
        return

    mw.progress.start(max=len(selected_nids), immediate=True)
    
    updated_count = 0
    skipped_count = 0
    
    try:
        for nid in selected_nids:
            note = mw.col.get_note(nid)
            
            if source_field not in note:
                skipped_count += 1
                mw.progress.update()
                continue
                
            if target_field not in note:
                 skipped_count += 1
                 mw.progress.update()
                 continue

            original_text = note[source_field]
            
            # Sentence Check
            if ignore_sentences and is_sentence(original_text):
                skipped_count += 1
                mw.progress.update()
                continue

            # Check overwrite
            if note[target_field] and not overwrite:
                skipped_count += 1
                mw.progress.update()
                continue

            # Local Lookup
            freq, error = get_frequency_local(original_text)
            
            if freq is not None:
                note[target_field] = str(freq)
                note.flush()
                updated_count += 1
            else:
                pass
            
            mw.progress.update(label=f"Processed {updated_count + skipped_count}/{len(selected_nids)}")
            mw.app.processEvents() 
            # No sleep needed for local lookup
            
    finally:
        mw.progress.finish()
        mw.reset()

    showInfo(f"Updated {updated_count} notes. Skipped {skipped_count}.")
