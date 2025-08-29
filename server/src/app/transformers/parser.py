from lark import Lark


with open('src/app/transformers/grammar.ebnf', 'r') as file:
    grammar = file.read()

parser = Lark(grammar)


def get_parser() -> Lark:
    return parser
