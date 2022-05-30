#!/usr/bin/env python3
import bibtexparser
import re
import argparse
import sys
import glob


def simplifiedString(input):
   return re.sub(r'\W+', '', input).lower()


def saveLookup(bibKey, bibEntry, lookup):
   year = bibEntry['year'] if 'year' in bibEntry else ''
   contentKey = simplifiedString(bibEntry['title']) + year
   if contentKey in lookup:
      raise Exception(f'Duplicate content key "{contentKey}"!')
   lookup[contentKey] = bibKey

   
def processTex(lines, oldLookup, newLookup):
   failed = set()
   for contentKey, oldBibTexKey in oldLookup.items():
      # Find new key through content comparison
      if contentKey not in newLookup:
         print(f'[!] Error replacing {oldBibTexKey}: Relevant entry not found in new bibliography (was it a duplicate?)', file=sys.stderr)
         failed.add(oldBibTexKey)
         continue
      newBibTexKey = newLookup[contentKey]
      try:
         # Find citation(s) for the current key and replace it only inside these sections
         lines, replacements = re.subn(r'(\\cite{[^\}]*)(' + oldBibTexKey + r')([^\}]*})', r'\1' + newBibTexKey + r'\3', lines)
         if replacements > 0:
            print(f'[>] Replaced {oldBibTexKey} -> {newBibTexKey} [{replacements} replacements]')
      except Exception as e:
         print(f'[!] Error replacing {oldBibTexKey}: {e}', file=sys.stderr)
         failed.add(oldBibTexKey)
   return lines, failed


if __name__ == '__main__':

   parser = argparse.ArgumentParser()
   parser.add_argument('--path', help='LaTeX input folder', type=str, required=True)
   parser.add_argument('--oldbib', help='Old (paper) bibliography file', 
      type=argparse.FileType('r', encoding='UTF-8'), required=True)
   parser.add_argument('--newbib', help='New (complete) bibliography file', 
      type=argparse.FileType('r', encoding='UTF-8'), required=True)
   parser.add_argument('--dry', help='Do not save output', dest='dry', action='store_true')

   args = parser.parse_args()

   oldBibliography = bibtexparser.load(args.oldbib, bibtexparser.bparser.BibTexParser(common_strings=True))
   newBibliography = bibtexparser.load(args.newbib, bibtexparser.bparser.BibTexParser(common_strings=True))
   args.oldbib.close()
   args.newbib.close()

   oldLookup = dict()
   newLookup = dict()

   for key, entry in oldBibliography.entries_dict.items():
      saveLookup(key, entry, oldLookup)

   for key, entry in newBibliography.entries_dict.items():
      saveLookup(key, entry, newLookup)

   # Replace BibTeX keys based on content keys
   failedKeys = set()
   for texPath in glob.glob(f'{args.path}/**/*.tex', recursive=True):
      converted = None
      with open(texPath, 'r') as f:
         print(texPath)
         converted, failed = processTex(f.read(), oldLookup, newLookup)
         failedKeys.update(failed)
      if args.dry:
         continue
      if converted:
         with open(texPath, 'w') as f:
            f.write(converted)
            print(f'---- Finished output to {texPath} with {len(failed)} failed keys ----')
      else:
         print(f'>>> ERROR: Failed to convert tex file {texPath}')
   print(f'Failed keys: {",".join(failedKeys)}') 
      
