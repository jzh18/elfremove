#!/usr/bin/python3
import sys
import os
import argparse
from shutil import copyfile

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../librarytrader'))

from librarytrader.librarystore import LibraryStore
from elf_remove_class import ELFRemove

parser = argparse.ArgumentParser(description='Remove unneccessary symbols of given librarys.')
parser.add_argument('json', help='the json file from libtrader')
parser.add_argument('-l', '--local', action="store_true", help='remove local functions')
parser.add_argument('--lib', nargs='*', help='list of librarys to be processed, use all librarys from json file if not defined')
parser.add_argument('--libonly', action="store_true", help='name of binary has to start with \'lib\'')
parser.add_argument('--addr_list', action="store_true", help='print list of addresses with size')

def log(mes):
    if(args.verbose):
        print(mes)

def proc():

    # get all unused symbol addresses
    store = LibraryStore()
    try:
        store.load(args.json)
    except Exception as e:
        print("Not a valid libtrader json file!")
        print(e)
        sys.exit(1)

    libobjs = store.get_library_objects()

    for lib in libobjs:

        # if no librarys where given -> use all
        if(args.lib and os.path.basename(lib.fullname) not in args.lib):
            continue
        if(args.libonly and not os.path.basename(lib.fullname).startswith("lib")):
            continue

        print("\nLibrary: " + lib.fullname)

        filename = lib.fullname

        # open library file as ELFRemove object
        elf_rem = None
        elf_rem = ELFRemove(filename)

        if(elf_rem.dynsym == None):
            print('dynsym table not found in File!')
            continue

        # get all blacklistet functions created by test script
        blacklist = []

        blacklist_file = "blacklist_" + os.path.basename(lib.fullname)
        if(os.path.exists(blacklist_file)):
            print("Found blacklist file for: " + os.path.basename(lib.fullname))
            with open(blacklist_file, "r") as file:
                blacklist_s = file.readlines()
            blacklist = [int(x.strip(), 10) for x in blacklist_s]

        # get all functions to remove from library
        addr = []
        for key in store[lib.fullname].exported_addrs.keys():
            if(key not in blacklist):
                value = store[lib.fullname].export_users[key]
                if(not value):
                    addr.append(key)

        # collect and remove local functions
        local = []
        if(args.local):
            for key in store[lib.fullname].local_functions.keys():
                # TODO all keys double -> as string and int, why?
                if(isinstance(key, str)):
                    continue
                if(key not in blacklist):
                    value = store[lib.fullname].local_users.get(key, [])
                    if(not value and key == 594912):
                        local.append((key, store[lib.fullname].ranges[key]))
            print(local)

        # collect the set of Symbols for given function names
        collection_dynsym = elf_rem.collect_symbols_by_address(elf_rem.dynsym, addr)
        if(elf_rem.symtab != None):
            collection_symtab = elf_rem.collect_symbols_by_name(elf_rem.symtab, elf_rem.get_collection_names(collection_dynsym))

        # display statistics
        if(args.addr_list):
            elf_rem.print_collection_addr(collection_dynsym)
        else:
            elf_rem.print_collection_info(collection_dynsym, True)
            elf_rem.print_collection_info(collection_dynsym, False)

if __name__ == '__main__':
    args = parser.parse_args()
    proc()
