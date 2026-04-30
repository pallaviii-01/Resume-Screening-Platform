import re

GENDER_WORDS = [
    "mr", "mrs", "ms", "miss", "sir", "madam",
    "he", "she", "his", "her", "him", "hers",
    "male", "female", "man", "woman", "boy", "girl"
]

def anonymize_resume(parsed_resume: dict) -> dict:
    """Return a copy of the parsed resume with identity fields removed."""
    anonymous = parsed_resume.copy()
    anonymous["name"] = "Candidate"
    anonymous["email"] = "hidden@anonymous.com"
    anonymous["phone"] = "XXXXXXXXXX"

    # Strip gender hints from raw text
    text = anonymous.get("raw_text", "")
    for word in GENDER_WORDS:
        text = re.sub(rf"\b{word}\b", "[redacted]", text, flags=re.IGNORECASE)
    anonymous["raw_text"] = text

    return anonymous