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

def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


with open('gamemdx.dll', 'r+b') as gamemdx:
        mm = mmap.mmap(gamemdx.fileno(), 0)
        pe = pefile.PE('gamemdx.dll', fast_load=True)

        title("Force enable fast/slow", None)
        mm.seek(mm.find((b'\x8B\x41\x48\xC3'), 0))
        patches(mm.tell(), mm.read(6), "B801000000C3", 1)

        title("Force background judgement", None)
        mm.seek(mm.find((b'\x8B\x41\x44\xC3'), 0))
        patches(mm.tell(), mm.read(6), "B801000000C3", 1)

        title("Force darkest background", None)
        mm.seek(mm.find((b'\x75\x03\x33\xC0\xC3\x8B\x41\x38'), 0))
        patches(mm.tell(), mm.read(4), "33C0B003", 1)

        title("Opaque background for darkest background option", "This makes the darkest background option be 99% opaque, hiding the dancers and videos.")
        mm.seek(mm.find((b'\x33\x33\x33\x3F\x66\x66\x66\x3F'), 0)+4)
        patches(mm.tell(), mm.read(3), "A4707D", 1)

        title("Song Unlock", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x06\x80\x38\x00\x0F'), 0)+4)
        if mm.tell() > 0x100:
            patches(mm.tell(), mm.read(2), "90E9", 2)
            mm.seek(mm.find((b'\x32\xC0'), mm.tell()))
            patches(mm.tell(), mm.read(2), "B001", 2)
            mm.seek(mm.find((b'\xB8\x00\x00\x00\x0F\x8C'), mm.tell())+4)
            patches(mm.tell(), mm.read(2), "90E9", 2)
        else:
            mm.seek(mm.find((b'\x75\x07\x32\xC0'), 0xCCCCC))
            patches(mm.tell(), mm.read(4), "9090B001", 2)
        mm.seek(mm.find(b'\x65\x76\x65\x6E\x74\x6E\x6F\x5F\x32', 0))
        patches(mm.tell(), mm.read(1), "62", 2)
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
        mm.seek(mm.find((b'\x0F\x95\xC0\x84\xC0\x75\x4A'), 0)+5)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Timer Freeze", None)
        mm.seek(mm.find((b'\xB0\x00\x00\x00\x74\x5B'), 0)+4)
        patches(mm.tell(), mm.read(1), "EB", 1)

        title("Unlock options (force premium start)", "Extended e-amusement exclusive options such as ARROW COLOR and 0.25 speed mod")
        print(f"    patches: [")
        try:
            mm.seek(mm.find((b'\x8B\xCB\xFF\x15\x92'), 0))
            if mm.tell() > 0x60000:
                patches(mm.tell(), mm.read(5), "E9AF000000", 2)
                is_old = True
            else:
                mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), 0))
                mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), mm.tell())+1)
                mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), mm.tell()))
                patches(mm.tell(), mm.read(5), "E976000000", 2)
                is_old = False
        except ValueError:
            mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), 0))
            mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), mm.tell())+1)
            mm.seek(mm.find((b'\x33\xD2\x41\x8B\xCC'), mm.tell()))
            patches(mm.tell(), mm.read(5), "E976000000", 2)
            is_old = False
        if is_old:
            mm.seek(mm.find((b'\x00\x00\x00\x49\x8B'), mm.tell())+1)
            mm.seek(mm.find((b'\x00\x00\x00\x49\x8B'), mm.tell())+1)
            mm.seek(mm.find((b'\x00\x00\x00\x49\x8B'), mm.tell())+1)
            mm.seek(mm.find((b'\x00\x00\x00\x49\x8B'), mm.tell())+3)
            patches(mm.tell(), mm.read(2), "EB44", 2)
        else:
            mm.seek(mm.find((b'\x00\x00\x00\x49\x8B'), mm.tell())+3)
            patches(mm.tell(), mm.read(2), "EB42", 2)
        print("    ],")
        print("},")

        title("Autoplay", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\x41\x8D\x50\x38\xE8'), 0)-2)
        patches(mm.tell(), mm.read(2), "9090", 2)
        mm.seek(mm.find((b'\x74'), mm.tell()))
        patches(mm.tell(), mm.read(2), "9090", 2)
        print("    ],")
        print("},")

        title("Hide all bottom text", "Such as EVENT MODE, PASELI, COIN, CREDIT, MAINTENANCE")
        try:
            mm.seek(mm.find((b'\x45\x56\x45\x4E\x54\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x00\x00\x46\x52\x45\x45\x20\x50\x4C\x41\x59\x00\x00\x00\x53\x00\x00\x00\x20\x00\x00\x00\x54\x4F\x4B\x45\x4E\x00\x00\x00\x43\x4F\x49\x4E\x00\x00\x00\x00\x00\x00\x00\x00\x25\x73\x25\x73\x3A\x25\x32\x64\x2F\x25\x32\x64\x00\x00\x00\x00\x43\x52\x45\x44\x49\x54\x25\x73\x3A\x25\x32\x64\x00\x00\x00\x00\x30\x30\x30\x30\x30\x00\x00\x00\x30\x30\x30\x30\x30\x30\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x20\x2B\x20\x25\x73\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x45\x58\x54\x52\x41\x20\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00\x4C\x4F\x43\x41\x4C\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x00\x00\x4F\x46\x46\x4C\x49\x4E\x45\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x4D\x41\x49\x4E\x54\x45\x4E\x41\x4E\x43\x45\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x00\x00\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x00\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x2E\x00\x4F\x4E\x4C\x49\x4E\x45\x00\x00\x45\x52\x52\x4F\x52\x00\x00\x00\x00\x00\x00\x00\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00'), 0))
            patches(mm.tell(), mm.read(328), "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)
        except ValueError:
            mm.seek(mm.find((b'\x45\x56\x45\x4E\x54\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x00\x00\x46\x52\x45\x45\x20\x50\x4C\x41\x59\x00\x00\x00\x53\x00\x00\x00\x20\x00\x00\x00\x54\x4F\x4B\x45\x4E\x00\x00\x00\x43\x4F\x49\x4E\x00\x00\x00\x00\x00\x00\x00\x00\x25\x73\x25\x73\x3A\x25\x32\x64\x2F\x25\x32\x64\x00\x00\x00\x00\x43\x52\x45\x44\x49\x54\x25\x73\x3A\x25\x32\x64\x00\x00\x00\x00\x30\x30\x30\x30\x30\x00\x00\x00\x30\x30\x30\x30\x30\x30\x00\x00\x2A\x2A\x2A\x2A\x2A\x2A\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x20\x2B\x20\x25\x73\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x45\x58\x54\x52\x41\x20\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00\x4C\x4F\x43\x41\x4C\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x00\x00\x4F\x46\x46\x4C\x49\x4E\x45\x20\x4D\x4F\x44\x45\x00\x00\x00\x00\x4D\x41\x49\x4E\x54\x45\x4E\x41\x4E\x43\x45\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x00\x00\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x00\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x00\x00\x00\x00\x00\x00\x43\x48\x45\x43\x4B\x49\x4E\x47\x2E\x2E\x2E\x00\x4F\x4E\x4C\x49\x4E\x45\x00\x00\x45\x52\x52\x4F\x52\x00\x00\x00\x00\x00\x00\x00\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00'), 0))
            patches(mm.tell(), mm.read(339), "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)

        title("Force Cabinet Type 6", "Gold cab")
        print(f"    patches: [")
        mm.seek(mm.find((b'\xBB\x02\x00\x00\x00'), 0)+1)
        mm.seek(mm.find((b'\xBB\x02\x00\x00\x00'), mm.tell())+1)
        patches(mm.tell(), mm.read(1), "06", 2)
        mm.seek(mm.find((b'\x0F\x88'), mm.tell()))
        patches(mm.tell(), mm.read(2), "90E9", 2)
        print("    ],")
        print("},")

        title("Enable cabinet lights for Cabinet Type 6", "This enables the use of cabinet lighting for Cabinet Type 6")
        print(f"    patches: [")
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\x48\x83\xEC\x28\xE8'), 0)+10)
        patches(mm.tell(), mm.read(3), "B80000", 2)
        mm.seek(mm.find((b'\x83\x61\x08\xFE\xE8'), 0)+4)
        patches(mm.tell(), mm.read(5), "B800000000", 2)
        mm.seek(mm.find((b'\x05\x00\x00\xE8'), mm.tell())+3)
        patches(mm.tell(), mm.read(5), "B800000000", 2)
        print("    ],")
        print("},")

        title("Enable DDR SELECTION", "Even works in offline/local mode!")
        mm.seek(mm.find((b'\xFF\xFF\xFF\x32\xC0\x48'), 0)+3)
        patches(mm.tell(), mm.read(2), "B001", 1)

        title("Premium Free", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\xFF\x41\x08'), 0))
        location = pe.get_rva_from_offset(mm.tell())
        while mm.read(1) != b'\x01':
            mm.seek(mm.tell()-2)
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(1), "00", 2)
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0))
        cc = pe.get_rva_from_offset(mm.tell())
        mm.seek(mm.find((b'\xFF\x41\x08'), 0))
        s = tohex((cc - location - 5), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        if len(result) == 3*2:
            result = result+'00'
        elif len(result) == 2*2:
            result = result+'0000'
        patches(mm.tell(), mm.read(6), f"E9{result}90", 2)
        s = tohex((location - (cc + 0xB) + 0x2), 32)[2:]
        result = "".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper()
        mm.seek(mm.find((b'\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0))
        patches(mm.tell(), mm.read(15), f"C74108010000004533C0E9{result}", 2)
        print("    ],")
        print("},")

        title("Mute Announcer", "Also mutes crowd cheering and booing during gameplay")
        print(f"    patches: [")
        mm.seek(mm.find((b'\x58\x85\xC9\x0F\x84'), 0)+3)
        patches(mm.tell(), mm.read(2), "90E9", 2)
        mm.seek(mm.find((str.encode('voice.xwb')), 0))
        patches(mm.tell(), mm.read(1), "62", 2)
        mm.seek(mm.find((str.encode('voice_n.xwb')), 0))
        patches(mm.tell(), mm.read(1), "62", 2)
        print("    ],")
        print("},")

        title("Force DDR SELECTION theme everywhere", "Skips intro and enables the skin selected below on all songs")
        print(f"    patches: [")
        mm.seek(mm.find((b'\x94\x01\x00\x00\x0F\x84'), 0)+4)
        patches(mm.tell(), mm.read(2), "90E9", 2)
        mm.seek(mm.find((b'\x0D\x75\x35'), 0)+1)
        patches(mm.tell(), mm.read(2), "9090", 2)
        mm.seek(mm.find((b'\x74'), mm.tell()))
        patches(mm.tell(), mm.read(1), "EB", 2)
        print("    ],")
        print("},")

        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose forced theme\",")
        find = mm.find((b'\xBA\x01\x00\x00\x00'), mm.tell())+1
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
        find = mm.find((b'\x45\xF8\x01\xE8'), 0)+3
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
        mm.seek(mm.find((b'\x4C\x0F\x45\xC9'), 0))
        mm.seek(mm.tell()-0x300)
        while mm.read(1) != b'\x75':
            mm.seek(mm.tell()-2)
        mm.seek(mm.tell()-1)
        patches(mm.tell(), mm.read(1), "EB", 2)
        mm.seek(mm.find((b'\x4C\x0F\x45\xC9'), mm.tell()))
        patches(mm.tell(), mm.read(4), "90909090", 2)
        mm.seek(mm.find((b'\x8B\x5C\x24'), mm.tell()))
        patches(mm.tell(), mm.read(12), "BBEF010000895C2438EB1F90", 2)
        mm.seek(mm.find((b'\xEB\x16'), mm.tell()))
        patches(mm.tell(), mm.read(12), "C7442438EF010000EB0E9090", 2)
        print("    ],")
        print("},")
