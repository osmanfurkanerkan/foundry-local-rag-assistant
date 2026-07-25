import re


def clean_text(text: str) -> str:
    """Fazla bosluk ve ust uste binen bos satirlari sadelestirir."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
