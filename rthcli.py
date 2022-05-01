#/usr/bin/env python3


from dataclasses import dataclass
import argparse
import sys
from rth.state import State
from rth.chain import Chain


@dataclass
class Stuff:
    args: argparse.Namespace
    state: State
    chain: Chain


def do_cat(stuff: Stuff):
    if stuff.args.mode == 'list':
        for short, category in sorted(stuff.state.categories.items()):
            print(short, category)


def do_thing(stuff: Stuff):
    if stuff.args.mode == 'list':
        for thing, category in sorted(stuff.state.things.items(), key=lambda x: (self.state.things[x[0]], x[1], x[0])):
            print(category, thing)

def do_count(stuff: Stuff):
    if stuff.args.mode == 'add':
        stuff.chain.add_thing(args.thing)
    elif stuff.args.mode == 'remove':
        stuff.chain.remove_thing(args.thing)
    elif stuff.args.mode == 'list':
        for thing, count in sorted(stuff.state.counts.items(), key=lambda x: (x[1], x[0])):
            if stuff.args.show_all or count > 0:
                print(thing, count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Do things with rth")
    subparsers = parser.add_subparsers(help="sub-command help")

    parser_cat = subparsers.add_parser('cat', help='work with categories')
    parser_cat.add_argument('--list', '-l', action='store_const', dest='mode', const='list')
    parser_cat.set_defaults(func=do_cat)

    parser_thing = subparsers.add_parser('thing', help='work with things')
    parser_thing.add_argument('--list', '-l', action='store_const', dest='mode', const='list')
    parser_thing.set_defaults(func=do_thing)

    parser_count = subparsers.add_parser('count', help='work with counts')
    parser_count.add_argument('--add', '-a', action='store_const', dest='mode', const='add')
    parser_count.add_argument('--remove', '-r', action='store_const', dest='mode', const='remove')
    parser_count.add_argument('--list', '-l', action='store_const', dest='mode', const='list')
    parser_count.add_argument('--show-all', '-A', action='store_true')
    parser_count.add_argument('thing', nargs='?')
    parser_count.set_defaults(func=do_count)

    args = parser.parse_args()

    state = State()
    state.load_categories('rth/data/categories')
    state.load_things('rth/data/things')

    with open('chain', 'r+', encoding='utf8') as cp:
        chain = Chain(state, cp)
        chain.load_previous()

        if not 'func' in args:
            sys.stderr.write('Please specify a subcommand\n')
            exit(-1)

        stuff = Stuff(args, state, chain)
        args.func(stuff)
