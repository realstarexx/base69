from __future__ import annotations
import sys
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Union

_logger = logging.getLogger("base69")
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_logger.setLevel(logging.INFO)


class Base69Error(Exception):
    pass


class InvalidCharacterError(Base69Error):
    def __init__(self, ch: str) -> None:
        super().__init__(f"Invalid Base69 character: {repr(ch)}")
        self.ch = ch


class InvalidInputError(Base69Error):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)


@dataclass(frozen=True)
class Base69Config:
    alphabet: str = (
        "ABCDEFGHJKLMNPQRSTUVWXYZ"
        "abcdefghijkmnopqrstuvwxyz"
        "23456789"
        "!$*+=?^~.#@&%"
    )
    preserve_leading_zero_bytes: bool = False

    @property
    def base(self) -> int:
        return len(self.alphabet)

    @property
    def cmap(self) -> Dict[str, int]:
        return {ch: i for i, ch in enumerate(self.alphabet)}


class Base69:
    def __init__(self, config: Optional[Base69Config] = None) -> None:
        self.config = config or Base69Config()
        self._alphabet = self.config.alphabet
        self._base = self.config.base
        self._cmap = self.config.cmap

    def encode(self, data: Union[bytes, bytearray]) -> str:
        if not isinstance(data, (bytes, bytearray)):
            raise InvalidInputError("encode expects bytes-like input")
        if len(data) == 0:
            return self._alphabet[0]
        n = self._bytes_to_int(data)
        s = self._int_to_string(n)
        if self.config.preserve_leading_zero_bytes:
            leading = len(data) - len(data.lstrip(b"\x00"))
            if leading > 0:
                s = self._alphabet[0] * leading + s
        return s

    def decode(self, text: str) -> bytes:
        if not isinstance(text, str):
            raise InvalidInputError("decode expects str input")
        if len(text) == 0:
            raise InvalidInputError("empty string")
        if self.config.preserve_leading_zero_bytes:
            leading = 0
            for ch in text:
                if ch == self._alphabet[0]:
                    leading += 1
                else:
                    break
            core = text[leading:]
            n = self._string_to_int(core) if core else 0
            raw = self._int_to_bytes(n)
            if leading:
                raw = b"\x00" * leading + raw
            return raw
        n = self._string_to_int(text)
        return self._int_to_bytes(n)

    def _bytes_to_int(self, data: bytes) -> int:
        total = 0
        for b in data:
            total = (total << 8) | b
        return total

    def _int_to_bytes(self, value: int) -> bytes:
        if value == 0:
            return b"\x00"
        length = (value.bit_length() + 7) // 8
        out = bytearray(length)
        for i in range(length - 1, -1, -1):
            out[i] = value & 0xFF
            value >>= 8
        return bytes(out)

    def _int_to_string(self, n: int) -> str:
        if n == 0:
            return self._alphabet[0]
        chars: List[str] = []
        base = self._base
        while n > 0:
            n, r = divmod(n, base)
            chars.append(self._alphabet[r])
        chars.reverse()
        return "".join(chars)

    def _string_to_int(self, s: str) -> int:
        acc = 0
        cmap = self._cmap
        for ch in s:
            if ch not in cmap:
                raise InvalidCharacterError(ch)
            acc = acc * self._base + cmap[ch]
        return acc


def b69encode(data: bytes) -> str:
    return Base69().encode(data)


def b69decode(text: str) -> bytes:
    return Base69().decode(text)
