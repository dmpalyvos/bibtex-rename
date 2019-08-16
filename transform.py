import bibtexparser
import re
import argparse
import sys


def simplifiedString(input):
   return re.sub(r'\W+', '', input).lower()


def saveLookup(bibKey, bibEntry, lookup):
   year = bibEntry['year'] if 'year' in bibEntry else ''
   contentKey = simplifiedString(bibEntry['title']) + year
   if contentKey in lookup:
      raise Exception(f'Duplicate content key "{contentKey}"!')
   lookup[contentKey] = bibKey


if __name__ == '__main__':

   parser = argparse.ArgumentParser()
   parser.add_argument('--tex', help='LaTeX input file', 
      type=argparse.FileType('r'), required=True)
   parser.add_argument('--oldbib', help='Old bibliography file', 
      type=argparse.FileType('r'), required=True)
   parser.add_argument('--newbib', help='New bibliography file', 
      type=argparse.FileType('r'), required=True)
   parser.add_argument('--out', help='Output LaTeX file', 
      type=argparse.FileType('w'), default='out.tex')

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
   text = args.tex.read()
   errorCount = 0
   for contentKey, oldBibTexKey in oldLookup.items():
      # Find new key through content comparison
      if contentKey not in newLookup:
         print(f'[!] Error replacing {oldBibTexKey}: Relevant entry not found in {args.newbib.name} (was it a duplicate?)', file=sys.stderr)
         errorCount += 1
         continue
      newBibTexKey = newLookup[contentKey]
      try:
         # Find citation(s) for the current key and replace it only inside these sections
         text, replacements = re.subn(r'(\\cite{[^\}]*)(' + oldBibTexKey + r')([^\}]*})', r'\1' + newBibTexKey + r'\3', text)
         print(f'[>] Replaced {oldBibTexKey} -> {newBibTexKey} [{replacements} replacements]')
      except Exception as e:
         print(f'[!] Error replacing {oldBibTexKey}: {e}', file=sys.stderr)
         errorCount += 1
   args.tex.close()

   try:
      # Write new TeX file   
      args.out.write(text)
      print(f'---- Finished output to {args.out.name} with {errorCount} errors ----')
   except Exception as e:
      raise e
   finally:
      args.out.close()