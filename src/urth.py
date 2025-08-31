#!/bin/env python

import logging
import os
import platform
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import ebooklib
import inflect
import typer
from bs4 import BeautifulSoup, PageElement
from ebooklib import epub
from pyglossary.entry_base import MultiStr
from pyglossary.glossary_v2 import Glossary
from typing_extensions import Annotated

logger = logging.getLogger("urth")

# constants
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
    soup = convert_epub_to_soup(input_path)
    save_soup(soup, input_path, output_path)
    result = process_input(soup)
    result = add_plurals(result)
    safe_write(result, output_path)


def configure_logger():
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)


def convert_epub_to_soup(input_path: Path) -> BeautifulSoup:
    book = epub.read_epub(str(input_path), options={"ignore_ncx": True})
    epub_soup = BeautifulSoup("", "html.parser")
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            epub_soup.extend(soup.body.contents)
    return epub_soup


def save_soup(soup: BeautifulSoup, input_path: Path, output_path: Path):
    html_filename = input_path.with_suffix(".html").name
    html_path = output_path.parent / html_filename
    html_path.write_text(soup.prettify(), encoding="utf-8")
    logger.info(f"Wrote raw HTML to {html_path}")


def process_input(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    result = []
    word: Optional[str] = None
    definition: List[str] = []
    for el in soup.find_all(True, recursive=False):
        # detect word
        current_word = get_word(el)
        if current_word:
            # flush previous word
            if word:
                result.append((word, join_definition(definition)))
            word = current_word
            definition.clear()
        # detect definition
        if word:
            current_definition = get_definition(el)
            if current_definition:
                definition.append(current_definition)
        if word == last_word:
            result.append((word, join_definition(definition)))
            break
    return result


def get_word(el: PageElement) -> Optional[str]:
    words = el.find_all(class_="bold", recursive=False)
    return merge(words)


def get_definition(el: PageElement) -> Optional[str]:
    words = el.find_all(class_="bold", recursive=False)
    for word in words:
        word.decompose()
    return el.get_text().strip() or None


def merge(els: List[PageElement]) -> Optional[str]:
    result = " ".join(el.get_text() for el in els)
    result = result.strip()
    return result or None


def join_definition(definitions: List[str]) -> str:
    return "<br>".join(definitions)


def add_plurals(defs: List[Tuple[str, str]]) -> List[Tuple[MultiStr, str]]:
    plural_engine = inflect.engine()
    new_defs: List[Tuple[MultiStr, str]] = []
    plural_count = 0
    for word, definition in defs:
        try:
            plural = plural_engine.plural(word)
        except:
            logger.warning("Failure while checking plural for %s", word)
            plural = None
        if plural and plural != word:
            key = [word, plural]
            plural_count += 1
        else:
            key = word
        new_defs.append((key, definition))
    logger.info("Added %d plural forms", plural_count)
    return new_defs


def safe_write(defs: List[Tuple[MultiStr, str]], output_path: Path):
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


def write(defs: List[Tuple[MultiStr, str]], workdir: Path):
    Glossary.init()

    glos = Glossary()
    for forms, defi in defs:
        glos.addEntry(
            glos.newEntry(
                forms,
                defi,
                defiFormat="h",  # html
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
