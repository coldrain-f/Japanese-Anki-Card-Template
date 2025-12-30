"""
JPDB Frequency Addon - Utility Functions
"""

import os
import re
from aqt import mw
from aqt.utils import showInfo, getFile


# Global cache for frequency map
_frequency_map = None
_frequency_file_path = None


def get_config():
    """Get addon configuration with defaults."""
    config = mw.addonManager.getConfig(__name__.split('.')[0])
    if config is None:
        config = {}

    # Ensure defaults
    defaults = {
        'source_field': 'Expression',
        'target_field': 'Frequency',
        'overwrite': False,
        'ignore_sentences': True,
        'frequency_file_path': ''
    }

    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    return config


def save_config(config):
    """Save addon configuration."""
    mw.addonManager.writeConfig(__name__.split('.')[0], config)


def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return text
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Decode common HTML entities
    clean = clean.replace('&nbsp;', ' ')
    clean = clean.replace('&lt;', '<')
    clean = clean.replace('&gt;', '>')
    clean = clean.replace('&amp;', '&')
    clean = clean.replace('&quot;', '"')
    return clean.strip()


def clear_frequency_cache():
    """Clear the cached frequency map."""
    global _frequency_map, _frequency_file_path
    _frequency_map = None
    _frequency_file_path = None
    showInfo("Frequency cache cleared.")


def select_frequency_file(browser=None):
    """Let user select a JPDB.txt file and save the path to config."""
    global _frequency_map, _frequency_file_path

    parent = browser if browser else mw
    file_path = getFile(
        parent,
        "Select JPDB.txt Frequency File",
        None,
        filter="Text Files (*.txt)"
    )

    if file_path:
        # Clear cache so it reloads with new file
        _frequency_map = None
        _frequency_file_path = None

        # Save to config
        config = get_config()
        config['frequency_file_path'] = file_path
        save_config(config)

        showInfo(f"Frequency file set to:\n{file_path}")
        return file_path

    return None


def load_frequency_map():
    """Load frequency map from JPDB.txt file."""
    global _frequency_map, _frequency_file_path

    if _frequency_map is not None:
        return _frequency_map

    config = get_config()
    file_path = config.get('frequency_file_path', '')

    # Check if configured path exists
    if file_path and os.path.exists(file_path):
        _frequency_file_path = file_path
    else:
        # Look in addon directory
        addon_dir = os.path.dirname(__file__)
        local_path = os.path.join(addon_dir, "JPDB.txt")

        if os.path.exists(local_path):
            _frequency_file_path = local_path
        else:
            # Ask user to select file
            file_path = getFile(
                mw,
                "Select JPDB.txt Frequency File",
                None,
                filter="Text Files (*.txt)"
            )

            if not file_path:
                return None

            _frequency_file_path = file_path

            # Save selected path to config
            config['frequency_file_path'] = file_path
            save_config(config)

    # Load the file
    freq_map = {}
    try:
        with open(_frequency_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('\t')
                if len(parts) >= 2:
                    word = parts[0]
                    rank = parts[1]
                    # Keep first occurrence (higher rank)
                    if word not in freq_map:
                        freq_map[word] = rank

        _frequency_map = freq_map
        return freq_map

    except Exception as e:
        showInfo(f"Error loading JPDB.txt: {str(e)}")
        return None


def is_sentence(text):
    """Check if text appears to be a sentence rather than a single word."""
    if not text:
        return False

    # Contains sentence punctuation
    if any(p in text for p in ['。', '、', '！', '？', '「', '」']):
        return True

    # Too long to be a single word
    if len(text) > 15:
        return True

    # Contains spaces (likely a phrase)
    if ' ' in text or '　' in text:
        return True

    return False


def get_frequency_local(text):
    """Look up frequency from local map."""
    freq_map = load_frequency_map()

    if not freq_map:
        return None, "File not loaded"

    # Strip HTML and whitespace
    clean_text = strip_html(text)

    if clean_text in freq_map:
        return freq_map[clean_text], None

    return None, "Not found in list"


def fill_frequency_for_selected_cards(browser):
    """Fill frequency data for selected cards in browser."""
    config = get_config()
    source_field = config.get('source_field', 'Expression')
    target_field = config.get('target_field', 'Frequency')
    overwrite = config.get('overwrite', False)
    ignore_sentences = config.get('ignore_sentences', True)

    # Ensure map is loaded before starting
    if not load_frequency_map():
        showInfo("Could not load JPDB.txt.\n\nPlease use 'Edit > JPDB Frequency > Select JPDB.txt File' to select your frequency file.")
        return

    selected_nids = browser.selectedNotes()

    if not selected_nids:
        showInfo("No notes selected.")
        return

    mw.progress.start(max=len(selected_nids), immediate=True)

    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    try:
        for idx, nid in enumerate(selected_nids):
            note = mw.col.get_note(nid)

            # Check source field exists
            if source_field not in note:
                skipped_count += 1
                mw.progress.update()
                continue

            # Check target field exists
            if target_field not in note:
                skipped_count += 1
                mw.progress.update()
                continue

            original_text = note[source_field]
            clean_text = strip_html(original_text)

            # Skip sentences if configured
            if ignore_sentences and is_sentence(clean_text):
                skipped_count += 1
                mw.progress.update()
                continue

            # Check overwrite setting
            if note[target_field] and not overwrite:
                skipped_count += 1
                mw.progress.update()
                continue

            # Look up frequency
            freq, error = get_frequency_local(clean_text)

            if freq is not None:
                note[target_field] = str(freq)
                mw.col.update_note(note)
                updated_count += 1
            else:
                not_found_count += 1

            mw.progress.update(
                value=idx + 1,
                label=f"Processing {idx + 1}/{len(selected_nids)}"
            )

    finally:
        mw.progress.finish()
        mw.reset()

    showInfo(
        f"Completed!\n\n"
        f"Updated: {updated_count}\n"
        f"Skipped: {skipped_count}\n"
        f"Not found: {not_found_count}"
    )
