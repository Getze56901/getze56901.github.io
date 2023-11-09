import mmap
import pefile
import struct

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

def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


with open('gamemdx.dll', 'r+b') as gamemdx:
        mm = mmap.mmap(gamemdx.fileno(), 0)
        pe = pefile.PE('gamemdx.dll', fast_load=True)

        title("Force enable fast/slow", None)
        mm.seek(mm.find((b'\x8B\x41\x44\xC3'), 0))
        patches(mm.tell(), mm.read(3), "31C040", 1)

        title("Force background judgement", None)
        mm.seek(mm.find((b'\x8B\x41\x40\xC3'), 0))
        patches(mm.tell(), mm.read(2), "31C0", 1)

        title("Force darkest background", None)
        mm.seek(mm.find((b'\x75\x03\x33\xC0\xC3\x8B\x41\x34\xC3'), 0))
        patches(mm.tell(), mm.read(4), "33C0B003", 1)

        title("Opaque background for darkest background option", "This makes the darkest background option be 99% opaque, hiding the dancers and videos.")
        mm.seek(mm.find((b'\x00\x00\x00\x00\x00\x00\x44\x40'), 0)+12)
        patches(mm.tell(), mm.read(3), "A4707D", 1)

        title("Song Unlock", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x80\x39\x00\x75\x08'), 0))
        while mm.read(1) != b"\x75":
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        off = mm.read(5)
        on_find = off[2:3].hex().upper()
        patches(mm.tell()-5, off, f"9090{on_find}B001", 2)
        mm.seek(mm.find((b'\x83\xC4\x0C\x03\xFE\x89\x7B\x34'), 0))
        while mm.read(1) != b"\x0F":
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(2), "90E9", 2)
        try:
            mm.seek(mm.find(b'\x65\x76\x65\x6E\x74\x6E\x6F\x5F\x32', 0))
            patches(mm.tell(), mm.read(1), "62", 2)
        except:
            pass
        mm.seek(mm.find(b'\x65\x76\x65\x6E\x74\x6E\x6F\x00'))
        patches(mm.tell(), mm.read(1), "62", 2)
        mm.seek(mm.find(b'\x72\x65\x67\x69\x6F\x6E\x00'))
        patches(mm.tell(), mm.read(1), "62", 2)
        mm.seek(mm.find(b'\x6C\x69\x6D\x69\x74\x65\x64\x5F\x63\x68\x61'))
        patches(mm.tell(), mm.read(1), "62", 2)
        mm.seek(mm.find(b'\x6C\x69\x6D\x69\x74\x65\x64\x00'))
        patches(mm.tell(), mm.read(1), "62", 2)
        print("    ],")
        print("},")

        title("Tutorial Skip", None)
        mm.seek(mm.find((b'\x8B\x08\x83\x39\x01\x74'), 0))
        while mm.read(3) != b'\x84\xC0\x75':
            mm.seek(mm.tell()+2)
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Timer Freeze", None)
        mm.seek(mm.find((b'\x7E\x05\xBE\x63'), 0))
        while mm.read(1) != b'\x74':
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Unlock options", "Extended e-amusement exclusive options such as ARROW COLOR and 0.25 speed mod")
        print(f"    patches: [")
        color = []
        patched = True
        while patched:
            mm.seek(mm.find((b'\x04\x00\x00\x00\x00\xE8'), mm.tell())+3)
            if (hex(mm.tell()-2)[2:].upper()) not in color and int(mm.tell()-2) > 1000 and int(mm.tell()-2) < 0x75000:
                color.append(hex(mm.tell()-2))
                patched = True
            else:
                patched = False
        patches(int(color[0], 16), (b'\x00'), "01", 2)
        patches(int(color[-1], 16), (b'\x00'), "01", 2)
        print("    ],")
        print("},")

        title("Autoplay", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x01\x00\x00\x74\x40\x6A\x34\xE8'), 0))
        while mm.read(1) != b'\x74':
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(2), "9090", 2)
        while mm.read(1) != b'\x74':
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(2), "9090", 2)
        print("    ],")
        print("},")

        title("Hide all bottom text", "Such as EVENT MODE, PASELI, COIN, CREDIT, MAINTENANCE")
        mm.seek(mm.find((b'\x45\x56\x45\x4E\x54\x20\x4D\x4F\x44\x45\x00\x00\x46\x52\x45\x45\x20\x50\x4C\x41\x59\x00\x00\x00\x53\x00\x00\x00\x20\x00\x00\x00\x54\x4F\x4B\x45\x4E\x00\x00\x00\x43\x4F\x49\x4E\x00\x00\x00\x00\x25\x73\x25\x73\x3A\x25\x32\x64\x2F\x25\x32\x64\x00\x00\x00\x00\x43\x52\x45\x44\x49\x54\x25\x73\x3A\x25\x32\x64\x00\x00\x00\x00\x30\x30\x30\x30\x30\x00\x00\x00\x30\x30\x30\x30\x30\x30\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x20\x2B\x20\x25\x73\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x45\x58\x54\x52\x41\x20\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00\x4C\x4F\x43\x41\x4C\x20\x4D\x4F\x44\x45\x00\x00\x4F\x46\x46\x4C\x49\x4E\x45\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x4D\x41\x49\x4E\x54\x45\x4E\x41\x4E\x43\x45\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x2E\x00\x4F\x4E\x4C\x49\x4E\x45\x00\x00\x45\x52\x52\x4F\x52\x00\x00\x00\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00'), 0))
        patches(mm.tell(), mm.read(288), "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)

        title("Force Cabinet Type 6", "Gold cab, some assets (such as menu background) may not work")
        mm.seek(mm.find((b'\x77\x78\xFF\x24\x85'), 0)+2)
        patches(mm.tell(), mm.read(2), "EB71", 1)

        title("Force blue menu background", None)
        mm.seek(mm.find((b'\xFF\x83\xF8\x06\x75'), 0)+4)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Enable cabinet lights for Cabinet Type 6", "This enables the use of cabinet lighting for Cabinet Type 6")
        print(f"    patches: [")
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x53\xE8'), 0)+10)
        patches(mm.tell(), mm.read(3), "B80000", 2)
        mm.seek(mm.find((b'\x8B\x00\x83\x60\x04\xFE\xE8'), 0)+6)
        patches(mm.tell(), mm.read(5), "B800000000", 2)
        mm.seek(mm.find((b'\x00\x80\x7C\x24\x12\x00\x0F\x85'), 0))
        while mm.read(1) != b'\xE8':
            mm.seek(mm.tell())
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(5), "B800000000", 2)
        print("    ],")
        print("},")

        title("Enable DDR SELECTION", "Even works in offline/local mode!")
        mm.seek(mm.find((b'\x07\x83\xC0\x04\x3B\xC1\x75\xF5\x3B\xC1\x0F\x95\xC0\x84\xC0\x75'), 0))
        while mm.read(2) != b'\x32\xC0':
            mm.seek(mm.tell())
        mm.seek(mm.tell()-2)
        patches(mm.tell(), mm.read(2), "B001", 1)

        title("Premium Free", None)
        mm.seek(mm.find((b'\xB9\x01\x00\x00\x00\x89\x0D'), 0)+1)
        patches(mm.tell(), mm.read(1), "00", 1)

        title("Mute Announcer", "Also mutes crowd cheering and booing during gameplay")
        print(f"    patches: [")
        mm.seek(mm.find((b'\xC6\x40\x85\xC0\x0F\x84'), 0)+4)
        patches(mm.tell(), mm.read(2), "90E9", 2)
        mm.seek(mm.find((str.encode('voice.xwb')), 0))
        patches(mm.tell(), mm.read(1), "62", 2)
        mm.seek(mm.find((str.encode('voice_n.xwb')), 0))
        patches(mm.tell(), mm.read(1), "62", 2)
        print("    ],")
        print("},")

        title("Force DDR SELECTION theme everywhere", "Skips intro and enables the skin selected below on all songs")
        print(f"    patches: [")
        mm.seek(mm.find((b'\x0F\x84\xF7\x00\x00\x00\x57\x8B\xFB'), 0))
        patches(mm.tell(), mm.read(2), "90E9", 2)
        mm.seek(mm.find((b'\xC9\x83\x7A\x10\x0D\x75'), 0)+5)
        patches(mm.tell(), mm.read(2), "9090", 2)
        mm.seek(mm.find((b'\xFF\xFF\xFF\x83\xF8\x04\x77'), mm.tell())+6)
        patches(mm.tell(), mm.read(2), "9090", 2)
        mm.seek(mm.find((b'\xFF\x24\x85'), mm.tell()))
        patches(mm.tell(), mm.read(2), "EB11", 2)
        print("    ],")
        print("},")

        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose forced theme\",")
        find = mm.find((b'\xC3\xB9\x02\x00\x00\x00\x89'), mm.tell())+2
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union("01", "1st", None)
        union("02", "EXTREME", None)
        union("03", "SuperNOVA2", None)
        union("04", "X2", None)
        union("05", "2013", None)
        print("    ]")
        print("},")

        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose cabinet type timing offset\",")
        find = mm.find((b'\x88\x5D\xF8\xE8'), 0)+3
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(5).hex().upper(), "Default", None)
        union("B800000000", "Force CRT 945 p3io timing", None)
        union("B801000000", "Force LCD 945 p3io timing", None)
        union("B802000000", "Force LCD HM64 p4io timing", None)
        union("B803000000", "Force CRT ADE-6291 p3io timing", None)
        union("B804000000", "Force LCD ADE-6291 p3io timing", None)
        union("B805000000", "Force LCD ADE-6291 p4io timing", None)
        union("B806000000", "Force LCD ADE-6291 bio2 timing", None)
        print("    ]")
        print("},")

        title("Center arrows for single player", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x7C\x24\x48\x39\x02\x75\x14'), 0)+5)
        patches(mm.tell(), mm.read(1), "EB", 2)
        mm.seek(mm.find((b'\x75\x05\xB8'), mm.tell()))
        patches(mm.tell(), mm.read(2), "9090", 2)

        # freeze_judge
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell()))
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x4C\x24\x1C'), mm.tell()))
        freeze = pe.get_rva_from_offset(mm.tell())
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0))
        cc = pe.get_rva_from_offset(mm.tell())
        s = tohex((cc - freeze - 5), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x4C\x24\x1C'), mm.tell()))
        patches(mm.tell(), mm.read(7), f"E9{result}9090", 2)
        s = tohex((freeze - (cc + 0x15) + 0x9), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        if len(result) == 3*2:
            result = result+'00'
        elif len(result) == 2*2:
            result = result+'0000'
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0))
        patches(mm.tell(), mm.read(19), f"83C40C8D4C241C36C701EF010000E9{result}", 2)

        # arrow
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), 0)+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell()))
        arrow = pe.get_rva_from_offset(mm.tell())
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), cc))
        cc2 = pe.get_rva_from_offset(mm.tell())
        s = tohex((cc2 - arrow - 5), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), 0)+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell())+1)
        mm.seek(mm.find((b'\x83\xC4\x0C\x8D\x44\x24\x1C'), mm.tell()))
        patches(mm.tell(), mm.read(7), f"E9{result}9090", 2)
        s = tohex((arrow - (cc2 + 0x15) + 0x9), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        if len(result) == 3*2:
            result = result+'00'
        elif len(result) == 2*2:
            result = result+'0000'
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), cc))
        patches(mm.tell(), mm.read(19), f"83C40C8D44241C36C700EF010000E9{result}", 2)
        print("    ],")
        print("},")

        print("{")
        print("    type : \"union\",")
        print("    name : \"Fullscreen FPS Target\",")
        mm.seek(mm.find((b'\xC7\x84\x24\x84\x00\x00\x00\x3C\x00\x00\x00'), 0)+7)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        for value in (60, 120, 144, 165, 240, 360):
            union(struct.pack('i', value).hex().upper(), f"{value} FPS", "Default" if value == 60 else None)
        print("    ]")
        print("},")
