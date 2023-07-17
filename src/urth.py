#!/bin/env python

import typer
import logging
from pathlib import Path
from pyglossary import Glossary
import shutil
from typing_extensions import Annotated
from typing import Dict

logger = logging.getLogger("urth")

# path constants
root = Path(__file__).resolve().parent.parent
out_dir = root / "out"
out_path = out_dir / "urth_mobipocket"
result_path = out_path / "OEBPS" / "content.mobi"
mobi_path = out_dir / "urth.mobi"

# other constants
last_word = "zoetic"

def main(
        input_path: Annotated[
            Path, 
            typer.Argument(
                exists=True, 
                file_okay=True,
                dir_okay=False,
                writable=False,
                readable=True,
                help="a path to the text version of Lexicon Urthus"
        )]):
    """
    Creates a Kindle compatible version of Lexicon Urthus, the dictionary for the Urth Cycle.
    
    The Urth Cycle is a science fiction series by Gene Wolfe.

    The Lexicon Urthus dictionary is a companion dictionary by Michael Andre-Driussi.

    Note that this script does not provide the actual dictionary, it's just a conversion script.
    """
    configure_logger()
    result = process_input(input_path)
    safe_write(result)

def configure_logger():
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

def process_input(input_path: Path) -> Dict[str, str]:
    result = {}
    text = input_path.read_text()
    arr = text.split("***")
    # skip everything before the first definition
    key = None
    value = None
    for segment in arr[1:]:
        token = segment.strip()
        if not key:
            if token:
                key = token
        else:
            truncated = token.split("\n\n\n")[0].strip()
            result[key] = truncated
            if key == last_word:
                break
            key = None
    return result

def safe_write(defs: Dict[str, str]):
    # preconditions
    if not defs:
        logger.warning("No definitions found, no mobi created")
        return
    logger.info("Parsed %d definitions", len(defs))
    if out_dir.exists():
        logger.warning("Out directory is dirty, cleaning.")
        shutil.rmtree(out_dir)
    logger.info("Writing dictionary...")
    # do the work
    write(defs)
    # check for success, and copy
    if result_path.exists():
        shutil.copy(result_path, mobi_path)
        relpath = mobi_path.relative_to(Path.cwd())
        logger.info("Successfully created %s", str(relpath))
    else:
        logger.warning("Some error occurred, no mobi was created")

def write(defs: Dict[str, str]):
    Glossary.init()

    glos = Glossary()
    for word, defi in defs.items():
        glos.addEntryObj(glos.newEntry(
            word,
            defi,
            defiFormat="m", # plain text
        ))

    glos.setInfo("title", "Lexicon Urthus")
    glos.setInfo("author", "Michael Andre-Driussi")
    glos.sourceLangName = "English"
    glos.targetLangName = "English"
    glos.write(str(out_path), format="Mobi")

if __name__ == "__main__":
    typer.run(main)
