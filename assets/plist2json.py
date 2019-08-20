#!/usr/bin/env python

import argparse
import base64
import collections
import datetime
import json
import plistlib
import sys
import tempfile
import xml.parsers.expat

def sanitize(obj):
    """Sanitize loaded plist object to a JSON-serializable one.
    Convert datetime.datetime (<date> tag) to an ISO 8601-formatted
    string, and bytes to base64 representation.
    """
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [sanitize(elem) for elem in obj]
    elif isinstance(obj, dict):
        return collections.OrderedDict((key, sanitize(val)) for key, val in obj.items())
    else:
        return obj

def plist2json_print(fp, filename=None):
    """Convert plist to JSON and print to stdout.
    fp is a readable and binary file object. filename is a descriptive
    name that is only used in error messages.
    An error message is printed to stderr if the input is not valid
    plist data.
    Returns 0 or 1 based on success or failure.
    """
    try:
        plistobj = sanitize(plistlib.load(fp, dict_type=collections.OrderedDict))
        print(json.dumps(plistobj, sort_keys=False, indent=4))
        sys.stdout.flush()
        return 0
    except (plistlib.InvalidFileException, xml.parsers.expat.ExpatError):
        msg = ("Error: '%s' is not a valid plist." % filename if filename is not None
               else "Error: Invalid plist.")
        print(msg, file=sys.stderr)
        sys.stderr.flush()
        return 1

def __selftest():
    """Test the sample plist from `man 5 plist'."""
    import contextlib, io, textwrap
    input = textwrap.dedent('''\
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
            "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Year Of Birth</key>
        <integer>1965</integer>
        <key>Pets Names</key>
        <array/>
        <key>Picture</key>
        <data>
            PEKBpYGlmYFCPA==
        </data>
        <key>City of Birth</key>
        <string>Springfield</string>
        <key>Name</key>
        <string>John Doe</string>
        <key>Kids Names</key>
        <array>
            <string>John</string>
            <string>Kyra</string>
        </array>
    </dict>
    </plist>
    ''')
    expected_output = textwrap.dedent('''\
    {
        "Year Of Birth": 1965,
        "Pets Names": [],
        "Picture": "PEKBpYGlmYFCPA==",
        "City of Birth": "Springfield",
        "Name": "John Doe",
        "Kids Names": [
            "John",
            "Kyra"
        ]
    }
    ''')
    output_buffer = io.StringIO()
    with tempfile.TemporaryFile() as fp:
        with contextlib.redirect_stdout(output_buffer):
            fp.write(input.encode('utf-8'))
            fp.seek(0)
            plist2json_print(fp)
    output = output_buffer.getvalue()
    if output == expected_output:
        print("Test passed", file=sys.stderr)
        return 0
    else:
        print("Error: Test failed\n\nExpected output:\n%s\nActual output:%s"
              % (expected_output, output), file=sys.stderr)
        return 1

def main():
    """CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("plistfiles", metavar="PLISTFILE", nargs="*")
    args = parser.parse_args()
    return_code = 0
    if args.plistfiles:
        for plistfile in args.plistfiles:
            try:
                with open(plistfile, "rb") as fp:
                    return_code |= plist2json_print(fp, filename=plistfile)
            except OSError:
                print("Error: Failed to open '%s'." % plistfile, file=sys.stderr)
                sys.stderr.flush()
                return_code = 1
    else:
        # plistlib.load requires seeking, so we write stdin to a temp
        # file first if seeking doesn't work on stdin
        if sys.stdin.seekable():
            return_code |= plist2json_print(sys.stdin.buffer, filename="<STDIN>")
        else:
            with tempfile.TemporaryFile() as fp:
                while True:
                    chunk = sys.stdin.buffer.read(1024)
                    if not chunk:
                        break
                    fp.write(chunk)
                fp.seek(0)
                return_code |= plist2json_print(fp, filename="<STDIN>")
    return return_code

if __name__ == "__main__":
    sys.exit(main())