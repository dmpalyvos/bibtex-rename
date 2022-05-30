# Rename BibTex References

## Introduction

This is is a simple tool that can automatically update your LaTeX code if you want to change the key format of your BibTex references.

For example, you have a document where the reference keys have the format `author_title_year` and you want to update the reference key format to `authorTitleYearJournalName`. Depending on the size of the document(s), changing all the references by hand can be quite tedious.

## Requirements

- python 3.6
- bibtexparser (`pip install bibtexparser`)

## Usage

The tool, `transform.py` a directory with LaTeX files, the original bibliography and the updated bibliography (with the new key format) and replaces the tex files in the directory with files whose reference keys have been updated to match the new bibliography. Use `--help` for more info on the CLI arguments.

## Tips & Tricks

- The tool uses the content of the bibliography entries (e.g., title, year) to determine the correct key association. Thus, to maximize your chances of success, try to not change the content of the the entries too much from your old to your new bibliography. You can always make any changes you want after updating they keys.
- The updated bibliography can be a superset of the original one. The tool should have no problem, as long as there are no entries that are very similar (e.g., same title and year).
- While I have tweaked the tool and it works good enough for my needs, feel free to submit a pull request if you run into any problems. :)
