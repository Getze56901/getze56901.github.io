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
 


with open('popn22.dll', 'r+b') as popn22:
        mm = mmap.mmap(popn22.fileno(), 0)
        pe = pefile.PE('popn22.dll', fast_load=True)

        title("E: Drive Fix", "Fix crash caused by no E: drive")
        mm.seek(mm.find((b'\x65\x3A\x2F'), 0))
        patches(mm.tell(), mm.read(3), "646576", 1)

        title("HDMI Audio Fix", None)
        mm.seek(mm.find((b'\x10\x85\xC0\x75\x96'), 0)+1)
        patches(mm.tell(), mm.read(4), "90909090", 1)

        title("Prevent Windows volume change on boot", "If your volume gets forced to max, turn this on")
        mm.seek(mm.find((b'\x10\x89\x44\x24\x14\x8B\xC6'), 0))
        while mm.read(2) != b"\x83\xEC":
            mm.seek(mm.tell()-3)
        mm.seek(mm.tell()-2)
        patches(mm.tell(), mm.read(1), "C3", 1)

        title("Boot to Event Mode", None)
        mm.seek(mm.find((b'\x8B\x00\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xC7\x40\x04\x00\x00\x00\x00'), 0))
        patches(mm.tell(), mm.read(4), "31C040C3", 1)

        title("Remove Timer", None)
        mm.seek(mm.find((b'\x00\x0F\x85\x65\x05\x00\x00'), 0)+1)
        patches(mm.tell(), mm.read(2), "90E9", 1)

        title("Skip Menu and Long Note Tutorials", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x00\x84\xC0\x74\x3A\xE8'), 0)+3)
        patches(mm.tell(), mm.read(1), "EB", 2)
        while mm.read(2) != b"\x75\x5E":
            mm.seek(mm.tell()-3)
        mm.seek(mm.tell()-2)
        patches(mm.tell(), mm.read(1), "EB", 2)
        mm.seek(mm.find((b'\x5F\x5E\x66\x83\xF8\x01\x75'), 0)+6)
        patches(mm.tell(), mm.read(1), "EB", 2)
        print("    ],")
        print("},")

        title("Unlock All Songs", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\xFF\xFF\xA9\x06\x00\x00\x68\x74'), 0)+7)
        patches(mm.tell(), mm.read(1), "EB", 2)
        while mm.read(2) != b"\x74\x13":
            mm.seek(mm.tell()-3)
        mm.seek(mm.tell()-2)
        patches(mm.tell(), mm.read(2), "9090", 2)
        print("    ],")
        print("},")

        title("Unlock EX Charts", None)
        print(f"    patches: [")
        ex = []
        patched = True
        mm.seek(0x200000)
        while patched:
            mm.seek(mm.find(b'\x80\x00\x00\x03', mm.tell())+1)
            if (hex(mm.tell()-2)[2:].upper()) not in ex and int(mm.tell()-2) > 0x200000:
                mm.seek(mm.tell()-1)
                patches(mm.tell(), mm.read(1), "00", 2)
                ex.append(hex(mm.tell()-1))
                patched = True
            else:
                patched = False
        patched = True
        mm.seek(0x200000)
        while patched:
            mm.seek(mm.find(b'\x80\x00\x00\x07', mm.tell())+1)
            if (hex(mm.tell()-2)[2:].upper()) not in ex and int(mm.tell()-2) > 0x200000:
                mm.seek(mm.tell()-1)
                patches(mm.tell(), mm.read(1), "00", 2)
                ex.append(hex(mm.tell()-1))
                patched = True
            else:
                patched = False
        print("    ],")
        print("},")

        title("Unlock Deco Parts", None)
        mm.seek(mm.find((b'\x83\x38\x00\x75\x22'), 0)+3)
        patches(mm.tell(), mm.read(2), "9090", 1)

        title("Unlock Characters", None)
        mm.seek(mm.find((b'\xA9\x50\x01\x00\x00\x74'), 0)+5)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Premium Free", "Score buffer never resets, use offline")
        print(f"    patches: [")
        mm.seek(mm.find((b'\xCC\xFE\x46\x0E\x80\xBE'), 0)+1)
        patches(mm.tell(), mm.read(3), "909090", 2)
        mm.seek(mm.find((b'\x75'), mm.tell()))
        patches(mm.tell(), mm.read(1), "EB", 2)
        mm.seek(mm.find((b'\x77\x3E'), mm.tell()))
        patches(mm.tell(), mm.read(2), "EB07", 2)
        print("    ],")
        print("},")

        title("Autoplay", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x84\xC0\x0F\x84\x08\x01\x00\x00'), 0)+2)
        patches(mm.tell(), mm.read(6), "909090909090", 2)
        mm.seek(mm.find((b'\x74\x53'), mm.tell()))
        patches(mm.tell(), mm.read(2), "9090", 2)
        print("    ],")
        print("},")

        title("Replace COLOR CHECK test menu with debug CHARA VIEWER", "Press service button to exit")
        mm.seek(mm.find(str.encode('COLOR CHECK'), 0))
        print(f"    patches: [")
        patches(mm.tell(), mm.read(13), "43484152412056494557455200", 2)
        mm.seek(mm.find((b'\x00\x00\x00\x00\x68\xAC\x00\x00\x00\xE8'), 0)+5)
        patches(mm.tell(), mm.read(3), "B0340C", 2)
        mm.seek(mm.find((b'\xE8\xDC\xFE\xFF\xFF'), mm.tell())+1)
        patches(mm.tell(), mm.read(4), "1CCD0900", 2)
        print("    ],")
        print("},")

        title("Replace SCREEN CHECK test menu with debug MUSIC INFO CHECKER", "Press service button to exit")
        mm.seek(mm.find(str.encode('SCREEN CHECK'), 0))
        print(f"    patches: [")
        patches(mm.tell(), mm.read(12), "4D5553494320494E464F0000", 2)
        mm.seek(mm.find((b'\x00\x00\x00\x00\x68\x8C\x00\x00\x00\xE8'), 0)+5)
        patches(mm.tell(), mm.read(3), "B0340C", 2)
        mm.seek(mm.find((b'\xE8\xFC\xFE\xFF\xFF'), mm.tell())+1)
        patches(mm.tell(), mm.read(4), "ACFB0900", 2)
        print("    ],")
        print("},")
