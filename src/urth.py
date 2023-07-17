#!/bin/env python

import typer
import logging
from pathlib import Path
from pyglossary import Glossary
import shutil

logger = logging.getLogger("urth")

# path constants
root = Path(__file__).resolve().parent.parent
out_dir = root / "out"
out_path = out_dir / "urth_mobipocket"
result_path = out_path / "OEBPS" / "content.mobi"
mobi_path = out_dir / "urth.mobi"

def main():
    configure_logger()
    safe_write()

def configure_logger():
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

def safe_write():
    # preconditions
    if out_dir.exists():
        logger.warning("Out directory is dirty, cleaning.")
        shutil.rmtree(out_dir)
    logger.info("Writing dictionary...")
    # do the work
    write()
    # check for success, and copy
    if result_path.exists():
        shutil.copy(result_path, mobi_path)
        relpath = mobi_path.relative_to(Path.cwd())
        logger.info("Successfully created %s", str(relpath))
    else:
        logger.warning("Some error occurred, no mobi was created")

def write():
    Glossary.init()

    glos = Glossary()
    mydict = {
        "a": "test1",
        "b": "test2",
        "c": "test3",
    }
    for word, defi in mydict.items():
        glos.addEntryObj(glos.newEntry(
            word,
            defi,
            defiFormat="m",  # "m" for plain text, "h" for HTML
        ))

    glos.setInfo("title", "Lexicon Urthus")
    glos.setInfo("author", "Michael Andre-Driussi")
    glos.sourceLangName = "English"
    glos.targetLangName = "English"
    glos.write(str(out_path), format="Mobi")

if __name__ == "__main__":
    typer.run(main)
