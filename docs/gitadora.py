import mmap
import pefile

def title(name, tooltip):
    print("{")
    print(f'    name: "{name}",')
    if tooltip is not None:
        print(f'    tooltip: "{tooltip}",')

def patches(poffset, off, on, pcount):

    poff = '[%s]' % ', '.join(map(str, ["0x"+(off.hex().upper()[i:i+2]) for i in range(0, len(off.hex().upper()), 2)]))
    pon = '[%s]' % ', '.join(map(str, ["0x"+(on[i:i+2]) for i in range(0, len(off.hex().upper()), 2)]))

    if pcount == 1:
        print(f"    patches: [{{ offset: 0x{hex(poffset)[2:].upper()}, off: {poff}, on: {pon} }}],")
        print("},")
    else:
        print(f"        {{ offset: 0x{hex(poffset)[2:].upper()}, off: {poff}, on: {pon} }},")

def union(on, name, tooltip):

    pon = '[%s]' % ', '.join(map(str, ["0x"+(on[i:i+2]) for i in range(0, len(on), 2)]))

    print("        {")
    print(f'            name : "{name}",')
    if tooltip is not None:
        print(f'            tooltip : "{tooltip}",')
    print(f"            patch : {pon},")
    print("        },")

with open('game.dll', 'r+b') as game:
        mm = mmap.mmap(game.fileno(), 0)
        pe = pefile.PE('game.dll', fast_load=True)

        title("Timer Freeze", None)
        mm.seek(mm.find((b'\x84\xC0\x0F\x85\x3E\x01\x00'), 0)+2)
        patches(mm.tell(), mm.read(2), "90E9", 1)

        title("Cursor Hold", None)
        mm.seek(mm.find((b'\x00\x85\xC9\x0F\x85'), 0)+3)
        patches(mm.tell(), mm.read(2), "90E9", 1)

        title("Stage Freeze", "Not compatible for use on networks")
        mm.seek(mm.find((b'\x00\x84\xC0\x0F\x85\x56\x01\x00'), 0)+3)
        patches(mm.tell(), mm.read(2), "90E9", 1)

        title("Skip Tutorial", "Not compatible for use on networks")
        mm.seek(mm.find((b'\x30\x83\xF8\x0D\x0F\x87'), 0)+4)
        patches(mm.tell(), mm.read(2), "90E9", 1)

        title("Unlock all songs", "Not compatible for use on networks")
        print(f"    patches: [")
        mm.seek(mm.find((b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x00\x61\x00\x02\x00\x00'), 0)+12)
        patches(mm.tell(), mm.read(2), "4D01", 2)
        mm.seek(mm.find((b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x00\x63\x00\x02\x00\x00'), mm.tell())+12)
        patches(mm.tell(), mm.read(2), "4D01", 2)
        mm.seek(mm.find((b'\xC3\x85\xC9\x75\x08'), 0)+3)
        patches(mm.tell(), mm.read(2), "EB11", 2)
        print("    ],")
        print("},")

        title("Enable Long Music", "Not compatible for use on networks")
        mm.seek(mm.find((b'\xCC\xCC\xCC\x80\x79\x30\x00\x74'), 0)+7)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Autoplay", "Not compatible for use on networks")
        print(f"    patches: [")
        mm.seek(mm.find((b'\x75\x16\xB9\x02\x00'), 0))
        patches(mm.tell(), mm.read(1), "EB", 2)
        mm.seek(mm.find((b'\x00\x0F\x85\xBA\x00\x00\x00\x48'), mm.tell())+1)
        patches(mm.tell(), mm.read(2), "90E9", 2)
        mm.seek(mm.find((b'\x00\x75\x60\x80'), mm.tell())+1)
        patches(mm.tell(), mm.read(1), "EB", 2)
        print("    ],")
        print("},")

        title("Skip 'NOW DATA INITIALIZING'", "Useful for testing only")
        mm.seek(mm.find((b'\x00\x00\x0F\x84\x74\x01\x00\x00'), 0)+2)
        patches(mm.tell(), mm.read(6), "909090909090", 1)
