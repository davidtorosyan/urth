#!/bin/env python

from pyglossary import Glossary

print("hello world")

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

glos.setInfo("title", "My Test StarDict")
glos.setInfo("author", "John Doe")
glos.write("out/test.mobi", format="Mobi")

print("done")
