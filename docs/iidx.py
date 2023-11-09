import mmap
import pefile

def title(name, tooltip):
    print("{")
    print(f'    name: "{name}",')
    if tooltip is not None:
        print(f'    tooltip: "{tooltip}",')

def patches(poffset, off, on, pcount):

    poff = '[%s]' % ', '.join(map(str, ["0x"+(off[i:i+2]) for i in range(0, len(off), 2)]))
    pon = '[%s]' % ', '.join(map(str, ["0x"+(on[i:i+2]) for i in range(0, len(off), 2)]))

    if pcount == 1:
        print(f"    patches: [{{ offset: 0x{poffset}, off: {poff}, on: {pon} }}],")
        print("},")
    else:
        print(f"        {{ offset: 0x{poffset}, off: {poff}, on: {pon} }},")

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

with open('bm2dx.dll', 'r+b') as bm2dx:
        mm = mmap.mmap(bm2dx.fileno(), 0)
        pe = pefile.PE('bm2dx.dll', fast_load=True)


        title("Standard/Menu Timer Freeze", None)
        find = mm.find((b'\xFF\xFF\x43\x58\x83\x7B\x50\x01\x7E\x03\xFF\x43\x5C\x48\x8D\x4B\x70\xE8'), 0)+0x20
        mm.seek(find)
        if mm.read(2).hex().upper() == "0F84":
            patches(hex(mm.tell()-2)[2:].upper(), "0F84", "90E9", 1)
        mm.seek(find)
        if mm.read(1).hex().upper() == "74":
            patches(hex(mm.tell()-1)[2:].upper(), "74", "EB", 1)

        title("Premium Free Timer Freeze", None)
        find = mm.find((b'\x40\x53\x48\x83\xEC\x20\x83\x79\x14\x00\x48\x8B\xD9\x7E'), 0)+0xD
        mm.seek(find)
        if mm.read(1).hex().upper() == "7E":
            patches(hex(mm.tell()-1)[2:].upper(), "7E", "EB", 1)

        title("Hide Time Limit Display on Results Screen", None)
        find = mm.find((b'\xFF\x33\xED\x84\xC0\x0F\x84'), 0)+0x3
        mm.seek(find)
        if mm.read(2).hex().upper() == "84C0":
            patches(hex(mm.tell()-2)[2:].upper(), "84C0", "9090", 1)

        title("Hide Background Color Banners on Song List", None)
        print(f"    patches: [")
        listb = []
        patched = True
        while patched:
            find = mm.find(str.encode('listb_'), mm.tell())+0x5
            mm.seek(find)
            if (hex(mm.tell()-2)[2:].upper()) not in listb and int(mm.tell()-2) > 1000:
                patches(hex(mm.tell())[2:].upper(), "5F", "00", 2)
                listb.append(hex(mm.tell()-2)[2:].upper())
                patched = True
            else:
                patched = False
        print("    ],")
        print("},")

        title("Cursor Lock", None)
        find = mm.find((b'\x08\x8B\xD8\xE8'), 0)
        mm.seek(find)
        find = mm.find((b'\x84\xC0\x74'), mm.tell())
        mm.seek(find+2)
        if mm.read(1).hex().upper() == "74":
            mm.seek(mm.tell()-1)
            patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)

        title("Unlock All Songs and Charts", None)
        find = mm.find((b'\x32\xC0\x48\x8B\x74\x24\x48\x48\x83\xC4\x30\x5F\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0)
        mm.seek(find)
        mm.seek(mm.find((b'\x32\xC0\x48\x8B\x74\x24\x48\x48\x83\xC4\x30\x5F\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), find+1))
        if mm.read(2).hex().upper() == "32C0":
            patches(hex(mm.tell()-2)[2:].upper(), "32C0", "B001", 1)

        title("CS-style Song Start Delay", 
        "Holding Start will pause the song at the beginning until you release it")
        try:
            find = mm.find((b'\x48\x8B\x01\x48\x8B\xD9\x8B'), 0)
            mm.seek(find)
            while mm.read(1) != b"\x7D":
                mm.seek(mm.tell())
            mm.seek(mm.tell()-1)
            if mm.read(1).hex().upper() == "7D":
                mm.seek(mm.tell()-1)
                patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)
        except:
            try:
                find = mm.find((b'\x48\x83\xEC\x20\x48\x8B\x11'), 0)
                mm.seek(find)
                while mm.read(1) != b"\x7D":
                    mm.seek(mm.tell())
                mm.seek(mm.tell()-1)
                if mm.read(1).hex().upper() == "7D":
                    mm.seek(mm.tell()-1)
                    patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)
            except:
                pass


        title("Show Lightning Model Folder in LDJ",
        "This folder is normally exclusive to TDJ mode")
        find = mm.find((b'\x44\x39\x60\x08\x75'), 0)+0x4
        mm.seek(find)
        if mm.read(1).hex().upper() == "75":
            mm.seek(mm.tell()-1)
            patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)

        title("Bypass Lightning Monitor Error", None)
        find = mm.find((b'\x0F\x85\xDF\x00\x00\x00\xF3'), 0)
        mm.seek(find)
        if mm.read(1).hex().upper() == "0F":
            mm.seek(mm.tell()-1)
            patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "90E9", 1)


        find = mm.find((b'\xB0\x01\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x48\x89\x4C\x24\x08'), 0)+16
        mm.seek(find)
        tdj = pe.get_rva_from_offset(mm.tell())

        title("Shim Lightning Mode IO (for spicetools)", None)
        print(f"    patches: [")
        find = mm.find((b'\x00\x48\xC7\x45\x20\xFE\xFF\xFF\xFF\x48\x89'), 0)
        mm.seek(find)
        find = mm.find((b'\x0F\x84'), mm.tell())
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "90E9", 2)
        find = mm.find((b'\xC1\x43\x0C\x83\xF8\x01\x75\x0B\x48\x8B\x4D\x98\x48\x8B\x01'), mm.tell())
        mm.seek(find)
        find = mm.find((b'\x00\x00\x00\xE8'), mm.tell())
        mm.seek(find+4)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-tdj+4), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), result, 2)
        print("    ]")
        print("},")


        title("Lightning Mode Camera Crash Fix (for spicetools)", None)
        find = mm.find((b'\xFF\x0F\x84\x8D\x00\x00\x00'), 0)+0x1
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(6).hex().upper(), "909090909090", 1)

        title("Force LDJ Software Video Decoder for All Boot Modes", None)
        find = mm.find((b'\xFF\x0F\x84\x8D\x00\x00\x00'), 0)-0x3
        mm.seek(find)
        if mm.read(1).hex().upper() == "02":
            mm.seek(mm.tell()-1)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "05", 1)


        title("Force Custom Timing and Adapter Mode in LDJ (Experimental)", "Enable this if the patch below is not default")
        print(f"    patches: [")
        find = mm.find((b'\x0F\x5B\xF6\x75\x0C'), 0)+0x3
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "EB", 2)
        find = mm.find((b'\xB8\x3C\x00\x00\x00\x74\x03'), 0)+0x5
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 2)
        print("    ]")
        print("},")


        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose Custom LDJ Timing/Adapter FPS\",")
        find = mm.find((b'\xDB\x3C\x00\x00\x00\xC7'), 0)+0x1
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(2).hex().upper(), "60 FPS", "Default")
        union("7800", "120 FPS", "Lightning")
        union("9000", "144 FPS", None)
        union("A500", "165 FPS", None)
        union("F000", "240 FPS", None)
        union("6801", "360 FPS", None)
        print("    ]")
        print("},")

        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose Custom TDJ Timing/Adapter FPS\",")
        find = mm.find((b'\xC7\x45\xDB\x78\x00\x00\x00'), 0)
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(36).hex().upper(), "120 FPS", "Default")
        union("C745DB90000000C7450B02000000488B45D74889450FC745D701000000C745DB90000000", "144 FPS", None)
        union("C745DBA5000000C7450B02000000488B45D74889450FC745D701000000C745DBA5000000", "165 FPS", None)
        union("C745DBF0000000C7450B02000000488B45D74889450FC745D701000000C745DBF0000000", "240 FPS", None)
        union("C745DB68010000C7450B02000000488B45D74889450FC745D701000000C745DB68010000", "360 FPS", None)
        print("    ]")
        print("},")


        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose Fullscreen Monitor Check FPS Target\",")
        print("    tooltip : \"Match with the two patches above if >120\",")
        find = mm.find((b'\x78\x00\x00\x00\xC7\x45'), 0)
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(2).hex().upper(), "120 FPS", "Default")
        union("9000", "144 FPS", None)
        union("A500", "165 FPS", None)
        union("F000", "240 FPS", None)
        union("6801", "360 FPS", None)
        print("    ]")
        print("},")

        title("Skip Monitor Check", None)
        find = mm.find((b'\x39\x87\x88\x00\x00\x00\x0F\x8C'), 0)+0x7
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "8D", 1)


        print("{")
        print("    type : \"union\",")
        print("    name : \"Choose Skip Monitor Check FPS\",")
        find = mm.find((b'\x44\x8B\x91\x48\x0B\x00\x00\x44\x8B\xCA\x4C\x8B\xD9\x41\x81\xC2\x67\x01\x00\x00\xB8\xB7\x60\x0B\xB6\x0F\x57'), 0)
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(27).hex().upper(), "Default", None)
        union("48B80000000000005E4066480F6EC0F20F58C8C3CCCCCCCCCCCCCC", "120.0000 FPS", None)
        union("48B8000000000000624066480F6EC0F20F58C8C3CCCCCCCCCCCCCC", "144.0000 FPS", None)
        union("48B8986E1283C0A2644066480F6EC0F20F58C8C3CCCCCCCCCCCCCC", "165.0860 FPS", None)
        union("48B80000000000006E4066480F6EC0F20F58C8C3CCCCCCCCCCCCCC", "240.0000 FPS", None)
        union("48B8000000000080764066480F6EC0F20F58C8C3CCCCCCCCCCCCCC", "360.0000 FPS", None)
        print("    ]")
        print("},")


        print("{")
        print("    type : \"number\",")
        print("    name : \"Monitor Adjust Offset\",")
        find = mm.find((b'\x80\x01\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), 0)+0x5
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    size : 4,")
        print("    min : -1000,")
        print("    max : 1000,")
        print("},")


        title("Skip CAMERA DEVICE ERROR Prompt", "Prevents the CAMERA DEVICE ERROR message from popping up on boot")
        find = mm.find((b'\x0F\x84\xAA\x00\x00\x00\xB9\x3C'), 0)+0x1
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "81", 1)

        title("Unscramble Touch Screen Keypad in TDJ", None)
        find = mm.find((b'\x4D\x03\xC8\x49\xF7\xF1\x89'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(6).hex().upper(), "909090909090", 1)

        title("Enable 1P Premium Free", None)
        find = mm.find((b'\x48\x89\x44\x24\x50\x33\xFF'), 0)
        mm.seek(find)
        find = mm.find((b'\xFF\x84\xC0\x75\x14\xE8'), mm.tell())+3
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "EB", 1)

        title("Enable 2P Premium Free", None)
        print(f"    patches: [")
        mm.seek(mm.find((b'\xBA\x01\x00\x00\x00'), mm.tell()))
        while mm.read(2) != b"\x84\xC0":
            mm.seek(mm.tell()-3)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 2)
        find = mm.find((b'\x74'), mm.tell())
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 2)
        print("    ]")
        print("},")

        title("Enable ARENA", None)
        for _ in range(2):
            find = mm.find((b'\x75'), mm.tell()+1)
            mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)

        title("Enable BPL BATTLE", None)
        for _ in range(2):
            find = mm.find((b'\x74'), mm.tell()+1)
            mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)

        title("All Notes Preview 12s", None)
        print(f"    patches: [")
        find = mm.find((b'\x05\x00\x00\x00\x84\xC0'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "0C", 2)
        find = mm.find((b'\x05\x00\x00\x00\x84\xC0'), mm.tell())
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "0C", 2)
        print("    ]")
        print("},")

        title("Dark Mode", None)
        find = mm.find((b'\x10\x48\x85\xC9\x74\x10'), 0)
        mm.seek(find)
        while mm.read(2) != b"\x84\xC0":
            mm.seek(mm.tell()-3)
        mm.seek(mm.tell()-2)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 1)

        title("Hide Measure Lines", None)
        find = mm.find((b'\x83\xF8\x04\x75\x37'), 0)+3
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "EB", 1)

        title("WASAPI Shared Mode (with 44100Hz)", None)
        find = mm.find((b'\xE6\x01\x45\x33'), 0)+1
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), "01", "00", 1)

        title("SSE4.2 Fix", None)
        find = mm.find((b'\x24\x24\xF3\x45\x0F\xB8\xD3\x41\x8B\xC2\x66\x44\x89\x54\x24\x22\x0F\xAF\xC2\x66'), 0)+2
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(3).hex().upper(), "909090", 1)

        title("Skip Decide Screen", None)
        find = mm.find((b'\x8B\xF8\xE8\x6B\x00\x00\x00\x48'), 0)+2
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(5).hex().upper(), "9090909090", 1)

        title("Quick Retry", None)
        find = mm.find((b'\x32\xC0\x48\x83\xC4\x20\x5B\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x0F'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "B001", 1)

        title("Disable News Sound", "Disables the sound played when news banners appear.")
        find = mm.find((b'\x73\x79\x73\x73\x64\x5F\x6E\x65\x77\x73\x5F\x63\x75\x74\x69\x6E\x5F\x73\x65'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(19).hex().upper(), "73797373645F64756D6D790000000000000000", 1)

        title("Increase Game Volume", "Ignore the in-game volume settings and use the maximum possible volume level. Especially helpful for TDJ which tends to be very quiet.")
        find = mm.find((b'\xD7\xFF\x90\x98\x00\x00\x00\x90'), 0)+1
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(6).hex().upper(), "909090909090", 1)

        title("QWERTY Keyboard Layout for Song Search", "Changes the touch keyboard layout from alphabetical to QWERTY in song and artist search menu (TDJ only)")
        find = mm.find((b'\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5A\x2D'), 0)
        try:
            mm.seek(find)
            patches(hex(mm.tell())[2:].upper(), "4142434445464748494A4B4C4D4E4F505152535455565758595A2D", "51574552545955494F504153444647484A4B4C2D5A584356424E4D", 1)
        except:
            pass


        title("Hide All Bottom Text", "Except for FREE PLAY")
        find = mm.find((b'\x43\x52\x45\x44\x49\x54\x3A\x20\x25\x64\x20\x43\x4F\x49\x4E\x3A\x20\x25\x64\x20\x2F\x20\x25\x64\x00\x00\x00\x00\x00\x00\x00\x00\x43\x52\x45\x44\x49\x54\x3A\x20\x25\x64\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x4E\x4F\x54\x20\x41\x56\x41\x49\x4C\x41\x42\x4C\x45\x00\x00\x00\x45\x58\x54\x52\x41\x20\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x64\x00\x00\x00\x00\x00\x00\x00\x00\x45\x58\x54\x52\x41\x20\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x64\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x25\x73\x00\x00\x00\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x2A\x2A\x2A\x2A\x2A\x2A\x00\x00\x20\x2B\x20\x25\x64\x00\x00\x00\x20\x2B\x20\x25\x73\x00\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x4E\x4F\x20\x41\x43\x43\x4F\x55\x4E\x54\x00\x00\x00\x00\x00\x00\x49\x4E\x53\x45\x52\x54\x20\x43\x4F\x49\x4E\x5B\x53\x5D\x00\x00\x50\x41\x53\x45\x4C\x49\x3A\x20\x2A\x2A\x2A\x2A\x2A\x2A\x20\x2B\x20\x30\x30\x30\x30\x30\x00\x00\x43\x52\x45\x44\x49\x54\x3A\x20\x39\x39\x20\x43\x4F\x49\x4E\x3A\x20\x39\x39\x20\x2F\x20\x31\x30'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), "4352454449543A20256420434F494E3A202564202F20256400000000000000004352454449543A202564000000000000504153454C493A204E4F5420415641494C41424C45000000455854524120504153454C493A2025640000000000000000455854524120504153454C493A2025730000000000000000504153454C493A202564000000000000504153454C493A202573000000000000504153454C493A202A2A2A2A2A2A0000202B202564000000202B202573000000504153454C493A204E4F204143434F554E54000000000000494E5345525420434F494E5B535D0000504153454C493A202A2A2A2A2A2A202B20303030303000004352454449543A20393920434F494E3A203939202F203130", "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 1)


        # TICKER OFFSET
        find = mm.find((b'\x41\xB8\x00\x02\x00\x00\x48\x8D\x0D'), 0)+0x6
        mm.seek(find)
        relative = int(pe.get_rva_from_offset(mm.tell()))
        s = mm.read(7).hex().upper()
        offset = int("0x"+("".join(map(str.__add__, s[-2::-2] ,s[-1::-2]))[1:-6]), 16)+0x7
        abosulte_ticker_offset = hex(relative+offset)

        # HIDDEN OFFSET
        find = mm.find((b'\x00\x00\x00\x20\x20\x00\x00'), 0)+0x3
        mm.seek(find)
        hidden = pe.get_rva_from_offset(mm.tell())


        find = mm.find((b'\x44\x0F\x45\xC8\x48\x8D\x05'), 0)+0x4
        mm.seek(find)
        pattern_offset = (relative+offset) - int(pe.get_rva_from_offset(mm.tell()+0x7))
        s = hex(pattern_offset)[2:]
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())


        print("{")
        print("    type : \"union\",")
        print("    name : \"Reroute FREE PLAY Text\",")
        find = mm.find((b'\x44\x0F\x45\xC8\x48\x8D\x05'), 0)+0x7
        mm.seek(find)
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(4).hex().upper(), "FREE PLAY", "Default")
        union(result, "Song Title/Ticker information", None)

        find = mm.find((b'\x44\x0F\x45\xC8\x48\x8D\x05'), 0)+0x4
        mm.seek(find)
        pattern_offset = (hidden) - int(pe.get_rva_from_offset(mm.tell()+0x7))
        s = hex(pattern_offset)[2:]
        result = ("".join(map(str.__add__, ("00"+s)[-2::-2] ,("00"+s)[-1::-2])).upper())

        find = mm.find((b'\x44\x0F\x45\xC8\x48\x8D\x05'), 0)+0x7
        mm.seek(find)
        union(result, "Hide", None)
        print("    ]")
        print("},")



        find = mm.find((b'\x00\xEB\x17\x4C\x8D\x05'), 0)+0x3
        mm.seek(find)
        pattern_offset = (relative+offset) - int(pe.get_rva_from_offset(mm.tell()+0x7))
        s = hex(pattern_offset)[2:]
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())

        title("Reroute PASELI: ****** Text To Song Title/Ticker Information", None)
        find = mm.find((b'\x00\xEB\x17\x4C\x8D\x05'), 0)+0x6
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(4).hex().upper(), result, 1)



        title("Debug Mode", "While in game, press F1 to enable menu.  (Disables Profile/Score saving)")
        find = mm.find((b'\xC3\xCC\xCC\xCC\x32\xC0\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'), 0)+4
        mm.seek(find)
        if mm.read(1).hex().upper() == "32":
            patches(hex(mm.tell()-1)[2:].upper(), "32C0", "B001", 1)



        title("Increase 'All Factory Settings' Buffer", "Enable this if the option below is not default")
        print(f"    patches: [")
        find = mm.find((b'\xFE\xFF\xFF\xFF\xB9\x48\x01\x00\x00\xE8'), 0)+0x5
        mm.seek(find)
        if mm.read(4).hex().upper() == "48010000":
            patches(hex(mm.tell()-4)[2:].upper(), "48010000", "22611400", 2)
        find = mm.find((b'\x48\x8B\xEA\xBA\x48\x01\x00\x00\x48'), 0)+0x4
        mm.seek(find)
        if mm.read(4).hex().upper() == "48010000":
            patches(hex(mm.tell()-4)[2:].upper(), "48010000", "22611400", 2)
        print("    ]")
        print("},")



        #AfpViewerScene
        find = mm.find((b'\x48\x8D\x8B\x90\x10\x10\x00\x33'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        afp = pe.get_rva_from_offset(mm.tell())

        #QproViewerScene
        find = mm.find((b'\x01\x00\x33\xC0\x48\x89\x83'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        qpro = pe.get_rva_from_offset(mm.tell())

        #SoundViewerScene
        find = mm.find((b'\x48\x89\x5C\x24\x68\x4C\x89\x33'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        soundv = pe.get_rva_from_offset(mm.tell())

        #TestICCardQCScene
        find = mm.find((b'\xFF\x48\x8D\x9F\xF8\x00'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        qc = pe.get_rva_from_offset(mm.tell())


        print("{")
        print("    type : \"union\",")
        print("    name : \"Reroute 'All Factory Settings' Test Menu\",")
        find = mm.find((b'\xFE\xFF\xFF\xFF\xB9\x48\x01\x00\x00\xE8'), 0)+0xA
        mm.seek(find)
        while mm.read(1) != b"\xE8":
            mm.seek(mm.tell())
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-afp+4), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(4).hex().upper(), "TestAllFactorySettingsScene", "Default")
        union(result, "AfpViewerScene", None)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-qpro), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        union(result, "QproViewerScene", None)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-soundv), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        union(result, "SoundViewerScene", None)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-qc), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        union(result, "TestICCardQCScene", None)
        print("    ]")
        print("},")


        #CustomizeViewerScene
        find = mm.find((b'\x00\x33\xD2\x41\xB8\x98\x00'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        custom = pe.get_rva_from_offset(mm.tell())

        #SoundRankingViewerScene
        find = mm.find((b'\x00\x48\x89\x5C\x24\x68\x48\x89\x2B'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        soundr = pe.get_rva_from_offset(mm.tell())

        #SystemSoundViewerScene
        find = mm.find((b'\x48\x89\x44\x24\x30\x89\x74\x24\x38\x0F\x28\x44\x24\x30\x66\x0F\x7F\x44\x24\x30\x45\x33\xC9\x4C\x8D\x44\x24\x30\x48\x8B\xD7\x48\x8D\x8F\x88\x00\x00\x00\xE8'), 0)
        mm.seek(find)
        while mm.read(2) != b"\xCC\xCC":
            mm.seek(mm.tell()-4)
        system = pe.get_rva_from_offset(mm.tell())




        print("{")
        print("    type : \"union\",")
        print("    name : \"Reroute 'I/O Check -> Camera Check -> 2D Code check' Test Menu\",")
        find = mm.find((b'\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x48\x83\xEC\x38\x48\xC7\x44\x24\x20\xFE\xFF\xFF\xFF\xB9\xD0\x01\x00\x00\xE8'), 0)+30
        mm.seek(find)
        while mm.read(2) != b"\xC8\xE8":
            mm.seek(mm.tell())
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-custom+4), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        print(f"    offset : 0x{hex(mm.tell())[2:].upper()},")
        print("    patches : [")
        union(mm.read(4).hex().upper(), "TestIOCheckQrCheckScene", "Default")
        union(result, "CustomizeViewerScene", None)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-soundr-1), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        union(result, "SoundRankingViewerScene", None)
        s = (tohex(-(pe.get_rva_from_offset(mm.tell())-system-1), 32)[2:]).upper()
        result = ("".join(map(str.__add__, ("0"+s)[-2::-2] ,("0"+s)[-1::-2])).upper())
        union(result, "SystemSoundViewerScene", None)
        print("    ]")
        print("},")


        title("Auto Play", None)
        find = mm.find((b'\xFD\xFF\x33\xC9\xC6\x80'), 0)+10
        mm.seek(find)
        if mm.read(1).hex().upper() == "00":
            patches(hex(mm.tell()-1)[2:].upper(), "00", "01", 1)


        title("Omnimix", None)
        print(f"    patches: [")
        find = mm.find((b'\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x40\x53\x48\x83\xEC\x20\x0F\xB6\xD9\xE8\x22\x01\x00\x00\x84\xC0\x74\x14\x0F\xB6\xCB\xE8\x16\x00\x00\x00\x84\xC0\x74\x08\xB0\x01\x48\x83\xC4\x20\x5B\xC3\x32\xC0\x48\x83\xC4\x20\x5B\xC3'), 0)
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(5).hex().upper(), "C6470558C3", 2)
        find = mm.find((b'\x66\x39\x48\x08\x7F'), 0)+4
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "9090", 2)
        find = mm.find(str.encode('mdata.ifs'), 0)+4
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(1).hex().upper(), "6F", 2)
        find = mm.find(str.encode('music_data.bin'), 0)+6
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(4).hex().upper(), "6F6D6E69", 2)
        find = mm.find(str.encode('music_title_yomi.xml'), 0)+12
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(4).hex().upper(), "6F6D6E69", 2)
        find = mm.find(str.encode('music_artist_yomi.xml'), 0)+13
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(4).hex().upper(), "6F6D6E69", 2)
        find = mm.find(str.encode('video_music_list.xml'), 0)+12
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(4).hex().upper(), "6F6D6E69", 2)
        find = mm.find((b'\x7C\xED\x32\xC0\xC3'), 0)+2
        mm.seek(find)
        patches(hex(mm.tell())[2:].upper(), mm.read(2).hex().upper(), "B001", 2)
        print("    ]")
        print("},")
