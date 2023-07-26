# urth

## Table of contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Usage](#usage)
- [License](#license)

## Introduction

`urth.py` is a script which converts the [_Lexicon Urthus_](https://www.siriusfiction.com/lexicon.html) to a Kindle friendly dictionary format.

### The Urth Cycle

_The Urth Cycle_ is a science fiction series written by **Gene Wolfe**, consisting of five books:
* _The Shadow of the Torturer_ (1980)
* _The Claw of the Conciliator_ (1981)
* _The Sword of the Lictor_ (1983)
* _The Citadel of the Autarch_ (1983)
* _The Urth of the New Sun_ (1987)

The first four books are known collectively as [_The Book of the New Sun_](https://en.wikipedia.org/wiki/The_Book_of_the_New_Sun).

Together with other books in the series, these make up _The Solar Cycle_.

### Lexicon Urthus

The aforementioned series is famous for its difficult vocabulary, which draws on many archaic English words.

The _Lexicon Urthus_ (1994) written by **Michael Andre-Driussi** is a helpful companion, and defines over 1300 terms.

Note that its best to reference the lexicon on rereads, since part of the Solar Cycle experience is being lost the first time around.

### E-Readers

E-Readers like the Amazon Kindle can reveal definitions by just holding your finger over a word.

This script converts the Lexicon Urthus into a format compatible with this feature for easy access.

Note that you still need to get the Lexicon Urthus yourself (in epub format) - this script doesn't contain any copyrighted material.

## Setup

Clone this repo.

Required dependencies:
* [python](https://www.python.org/) 3.11 or higher
* [pyglossary](https://github.com/ilius/pyglossary)
* [kindlegen](https://wiki.mobileread.com/wiki/KindleGen)
* [typer](https://typer.tiangolo.com/)
* [ebooklib](https://github.com/aerkalov/ebooklib)
* [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/)

Note that if you're on Arch Linux you can install all of these from AUR.

Also note that `kindlegen` needs to be in the PATH.

## Usage

Run:

```sh
python src/urth.py path/to/lexicon_urthus.epub path/to/urth.mobi
```

If successful, this will save the converted dictionary to `urth.mobi`.

You can transfer this to your Kindle with a program like [Calibre](https://calibre-ebook.com/).

When you look up a word's definition, click the dictionary selector on the bottom right of the pop-up to select the Lexicon Urthus.

## Development

Formatted using [black](https://github.com/psf/black) and imports sorted with [isort](https://github.com/PyCQA/isort), both from VS Code.

## License
[MIT](https://choosealicense.com/licenses/mit/)
