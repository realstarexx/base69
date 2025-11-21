import sys
import argparse
import base64
from .resolver import b69encode, b69decode


def _read_input(value: str) -> bytes:
    try:
        with open(value, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return value.encode()


def cli():
    parser = argparse.ArgumentParser(prog="base69", description="Base69 encoder/decoder")
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode")
    enc.add_argument("input")

    dec = sub.add_parser("decode")
    dec.add_argument("input")

    args = parser.parse_args()

    if args.command == "encode":
        data = _read_input(args.input)
        print(b69encode(data))
        return

    if args.command == "decode":
        try:
            raw = _read_input(args.input)
            text = raw.decode().strip()
        except Exception:
            text = args.input.strip()

        out = b69decode(text)

        try:
            print(out.decode("utf-8"))
        except UnicodeDecodeError:
            print(base64.b64encode(out).decode())
        return


if __name__ == "__main__":
    cli()
