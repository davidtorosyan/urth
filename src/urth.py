#!/bin/env python

import logging
import os
import platform
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional

import ebooklib
import typer
from bs4 import BeautifulSoup
from ebooklib import epub
from pyglossary.glossary_v2 import Glossary
from typing_extensions import Annotated

logger = logging.getLogger("urth")

# constants
delim = "***"
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
            help="a path to the epub version of Lexicon Urthus",
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Argument(
            exists=False, help="a path to save the Kindle compatible mobi version"
        ),
    ],
):
    """
    Creates a Kindle compatible version of Lexicon Urthus, the dictionary for the Urth Cycle.

    The Urth Cycle is a science fiction series by Gene Wolfe.

    The Lexicon Urthus dictionary is a companion dictionary by Michael Andre-Driussi.

    Note that this script does not provide the actual dictionary, it's just a conversion script.
    """
    configure_logger()
    text = convert_epub_to_text(input_path)
    result = process_input(text)
    safe_write(result, output_path)


def configure_logger():
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)


def convert_epub_to_text(input_path: Path) -> str:
    arr = []
    book = epub.read_epub(str(input_path), options={"ignore_ncx": True})
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            keys = soup.find_all(class_="bold")
            for key in keys:
                key.insert_before(delim)
                key.insert_after(delim)
            arr.append(soup.get_text())
    return "\n".join(arr)


def process_input(text: str) -> Dict[str, str]:
    result = {}
    arr = text.split(delim)
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


def safe_write(defs: Dict[str, str], output_path: Path):
    if not defs:
        logger.warning("No definitions found, no mobi created")
        return
    logger.info("Parsed %d definitions", len(defs))
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        workdir = tmpdir / "urth_mobipocket"
        result_path = workdir / "OEBPS" / "content.mobi"
        # do the work
        logger.info("Writing dictionary...")
        write(defs, workdir)
        # check for success, and copy
        if result_path.exists():
            shutil.copy(result_path, output_path)
            logger.info("Successfully created %s", str(output_path))
        else:
            logger.warning("Some error occurred, no mobi was created")


def write(defs: Dict[str, str], workdir: Path):
    Glossary.init()

    glos = Glossary()
    for word, defi in defs.items():
        glos.addEntry(
            glos.newEntry(
                word,
                defi,
                defiFormat="m",  # plain text
            )
        )

    glos.setInfo("title", "Lexicon Urthus")
    glos.setInfo("author", "Michael Andre-Driussi")
    glos.sourceLangName = "English"
    glos.targetLangName = "English"
    glos.write(
        str(workdir),
        formatName="Mobi",
        kindlegen_path=get_kindlegen_path(),
    )


def get_kindlegen_path() -> Optional[str]:
    if platform.system() == "Windows":
        return _get_windows_kindlegen_path()
    return None


def _get_windows_kindlegen_path() -> Optional[str]:
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        return None
    exe_path = (
        Path(local_appdata) / "Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe"
    )
    if not exe_path.exists():
        return None
    return str(exe_path)


if __name__ == "__main__":
    typer.run(main)
