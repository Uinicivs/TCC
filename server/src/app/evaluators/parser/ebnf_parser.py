from lark import Lark


with open('grammar.lark', 'r') as file:
    grammar = file.read()

parser = Lark(grammar)


def get_parser() -> Lark:
    return parser
