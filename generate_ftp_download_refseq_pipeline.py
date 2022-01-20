#!/usr/bin/env python3

# The MIT License
# Copyright (c) 2021 Adrian Tan <adrian_tan@nparks.gov.sg>
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permsit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Modified to suit Kraken2's database structure

import os
import argparse
import subprocess
import textwrap
import re
import sys

def main():
    cwd = os.getcwd() # must be in $DB_NAME/
               
    parser = argparse.ArgumentParser(
         description='Download refseq database',
         formatter_class=argparse.RawDescriptionHelpFormatter,
         epilog=textwrap.dedent('''\
           usage: generate_download_refseq_db_pipeline -m <make_file> -d <database>

           database  archaea|bacteria|fungi|invertebrate|
                     mitochondrion|plant|plasmid|protozoa|plastid|
                     viral|vertebrate_mammalian|vertebrate_other 
           '''))
    parser.add_argument('-m', '--make_file', help='make file name', type=str, default='download_refseq_db.mk')
    parser.add_argument('-d', '--database', help='refseq database to download', type=str)
    parser.add_argument('-o', '--output_directory', help='output directory', type=str, default=os.path.join(cwd, 'sequences'))
    args = parser.parse_args()

    for arg in vars(args):
        print('\t{0:<20} :   {1:<10}'.format(arg, getattr(args, arg) or ''))
        
    #check on database validity
    if args.database not in ['archaea', 'bacteria', 'fungi', 'invertebrate', 
                             'mitochondrion', 'plant', 'plasmid', 'protozoa', 'plastid',
                             'viral', 'vertebrate_mammalian', 'vertebrate_other']:
        print('error : database not valid\n', file=sys.stderr)
        parser.print_help()
        exit()      

    pg = PipelineGenerator(args.make_file)
    
    try:
        os.makedirs(args.output_directory, exist_ok=True)
    except OSError as error:
        print(f'Directory {args.output_directory} cannot be created')    
        
    #get listing of files to download
    #curl https://ftp.ncbi.nlm.nih.gov/refseq/release/invertebrate/ > invertebrate.txt
    print('Getting directory listings')
#    print(f'curl https://ftp.ncbi.nlm.nih.gov/refseq/release/{args.database}/')
    out = subprocess.run(['curl', f'https://ftp.ncbi.nlm.nih.gov/refseq/release/{args.database}/'], text=True, capture_output=True)

    files = []
    for line in out.stdout.splitlines():
        m = re.search('>(.+genomic.fna.gz)<', line)
        if m != None:
#            print(line)
#            print(m.group(1))
            files.append(m.group(1))
    
    
    #generate make file        
    print('Generating pipeline')
    for file in files:
#        print(file)
        err = f'{args.output_directory}/{file}.err' 
        tgt = f'{args.output_directory}/{file}.OK' 
        dep = ''
        cmd = f'wget https://ftp.ncbi.nlm.nih.gov/refseq/release/{args.database}/{file} -P {args.output_directory} 2> {err}'
        pg.add(tgt, dep, cmd)

    #write make file
    print('Writing pipeline')
    pg.write()


class PipelineGenerator(object):
    def __init__(self, make_file):
        self.make_file = make_file 
        self.tgts = []
        self.deps = []
        self.cmds = []

    def add(self, tgt, dep, cmd):
        self.tgts.append(tgt)
        self.deps.append(dep)
        self.cmds.append(cmd)

    def print(self):
        print('.DELETE_ON_ERROR:')
        for i in range(len(self.tgts)):
            print(f'{self.tgts[i]} : {self.deps[i]}')
            print(f'\t{self.cmds[i]}')
            print(f'\ttouch {self.tgts[i]}')
        
    def write(self):
        f = open(self.make_file, 'w')
        f.write('.DELETE_ON_ERROR:\n\n')
        f.write('all : ')
        for i in range(len(self.tgts)):
            f.write(f'{self.tgts[i]} ')
        f.write('\n\n')
            
        for i in range(len(self.tgts)):
            f.write(f'{self.tgts[i]} : {self.deps[i]}\n')
            f.write(f'\t{self.cmds[i]}\n')
            f.write(f'\ttouch {self.tgts[i]}\n\n')
        f.close()        

main()
