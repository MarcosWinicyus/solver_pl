import streamlit as st
import json
import os

# --- Configuration ---
LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")

# Default display names for known codes
DISPLAY_NAMES = {
    "pt": "Português",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano"
}

# Global storage for loaded languages
STRINGS = {}
AVAILABLE_LANGUAGES = {}  # Format: {"code": "Display Name"}


def load_languages():
    """
    Loads all JSON translation files from the 'locales' directory.
    Updates STRINGS and AVAILABLE_LANGUAGES globals.
    """
    global STRINGS, AVAILABLE_LANGUAGES
    STRINGS = {}
    AVAILABLE_LANGUAGES = {}
    
    if not os.path.exists(LOCALES_DIR):
        # Fallback/Safety: Create directory if it doesn't exist
        try:
           os.makedirs(LOCALES_DIR)
        except OSError:
           pass
        return

    # iterate over JSON files
    for filename in sorted(os.listdir(LOCALES_DIR)):
        if filename.endswith(".json"):
            lang_code = filename[:-5]
            try:
                file_path = os.path.join(LOCALES_DIR, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    STRINGS[lang_code] = json.load(f)
                
                # Set display name (default to Upper Code if unknown)
                AVAILABLE_LANGUAGES[lang_code] = DISPLAY_NAMES.get(lang_code, lang_code.upper())
            except Exception as e:
                print(f"Error loading language file {filename}: {e}")

# Perform initial load on module import
load_languages()


def t(key_path: str) -> any:
    """
    Retrieves a string or object from the dictionary based on the current language.
    Usage: t("home.title")
    """
    # Default to 'pt' if language not set
    current_lang = st.session_state.get("language", "pt")
    
    # Fallback to 'pt' if current_lang is not loaded
    if current_lang not in STRINGS:
        current_lang = "pt"
        # If 'pt' is also missing (e.g. only 'en.json' exists), take the first available
        if "pt" not in STRINGS and STRINGS:
             current_lang = list(STRINGS.keys())[0]
    
    keys = key_path.split(".")
    
    # Start with the language dictionary
    value = STRINGS.get(current_lang, {})
    
    # Traverse keys
    for k in keys:
        if isinstance(value, dict):
             value = value.get(k, None)
        else:
             return f"[{key_path}]" # Key nesting error
        
        if value is None:
            return f"[{key_path}]" # Key not found
            
    return value


def get_available_languages():
    """Returns the dictionary of available languages, reloading from disk to catch new files."""
    load_languages()
    return AVAILABLE_LANGUAGES
