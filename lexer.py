import string
from typing import List, Optional

from common import Token, TokenKind, Keyword


SINGLE_CHAR_TOKENS = {
    ',': TokenKind.Comma,
    '=': TokenKind.Eq,
    '+': TokenKind.Plus,
    '(': TokenKind.LParen,
    ')': TokenKind.RParen,
    '[': TokenKind.LBrack,
    ']': TokenKind.RBrack,
    '{': TokenKind.LBrace,
    '}': TokenKind.RBrace,
    '!': TokenKind.Excl,
    ';': TokenKind.Semi,
}

MULTI_CHAR_TOKENS = (
    (string.ascii_letters + '_', TokenKind.Word, str),
    (string.digits, TokenKind.Int, int),
)


class LexingError(Exception):
    pass


def peek(src: str, i: int, d: int) -> Optional[str]:
    return src[i + d] if i + d < len(src) else None


def consume(src: str, i: int, chars: str) -> int:
    j = i
    while j < len(src) and src[j] in chars:
        j += 1
    return j - i


def lex(src: str) -> List[Token]:
    i = 0
    tokens: List[Token] = []
    while i < len(src):
        c = peek(src, i, 0)
        if c is None:
            break
        elif c == '#':
            while src[i] != '\n' and i < len(src):
                i += 1
        elif c in string.whitespace:
            i += 1
            continue
        elif c in SINGLE_CHAR_TOKENS:
            token_kind = SINGLE_CHAR_TOKENS[c]
            tokens.append(Token(token_kind, i, None))
            i += 1
        else:
            for chars, token_kind, post_processor in MULTI_CHAR_TOKENS:
                if c not in chars:
                    continue
                length = consume(src, i, chars)
                value = post_processor(src[i:i + length])
                tokens.append(Token(token_kind, i, value))
                i += length
                break
            else:
                raise LexingError(f'Unknown symbol: {c}')
    for token in tokens:
        if token.kind == TokenKind.Word:
            assert isinstance(token.value, str)
            kw = Keyword.from_str(token.value)
            if kw is None:
                continue
            token.kind = TokenKind.Keyword
            token.value = kw
    return tokens
