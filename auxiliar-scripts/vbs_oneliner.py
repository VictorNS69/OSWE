import sys
import os
import re
import base64
import urllib.parse


def convert_to_oneliner(vbscript):
    content = open(vbscript, "rt").read()
    content = re.sub(r" _.*?\n", " ", content)  # remove continuation lines (with leading space)
    content = (
        content
        .replace("\r\n", ":")       # Windows line endings to colon separator
        .replace("\r", "")          # strip remaining carriage returns
        .replace("\t", "")          # strip tabs
        .replace("\n", ":")         # remaining newlines to colon separator
    )
    # replace :: multiple times until no more remain
    while "::" in content:
        content = content.replace("::", ":")
    return content

def main():
    if len(sys.argv) != 2:
        print(f"(+) usage: {sys.argv[0]} <file.vbs>")
        sys.exit(1)

    vbscript = sys.argv[1]

    if not os.path.isfile(vbscript):
        print(f"[-] File not found: {vbscript}")
        sys.exit(1)

    base, ext = os.path.splitext(vbscript)
    out_file = f"{base}_oneliner{ext}"

    oneliner = convert_to_oneliner(vbscript)

    with open(out_file, "wt") as f:
        f.write(oneliner)

    print(f"[+] Oneliner saved to: {out_file}")

    # base64 encode then URL encode the oneliner
    b64 = base64.b64encode(oneliner.encode()).decode()
    url_encoded = urllib.parse.quote(b64)
    print(f"[+] Base64 + URL encoded:\n{url_encoded}")

if __name__ == "__main__":
    main()
