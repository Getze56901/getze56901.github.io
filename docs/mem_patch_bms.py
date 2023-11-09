import mmap
import pefile

def create_patch(infile, outfile, game_version):

    with open(infile, 'r+b') as bm2dx:
        with open(outfile, 'w', newline='\r\n') as patches:
            mm = mmap.mmap(bm2dx.fileno(), 0)
            pe = pefile.PE(infile, fast_load=True)

            ver = '0' if game_version % 2 == 0 else '1'

            print('# === BMS changes. DO NOT TOUCH!! ===', file=patches)

            # Z rev
            mm.seek(mm.find(b'\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x40\x53\x48\x83\xEC\x20\x0F\xB6\xD9\xE8\x22\x01\x00\x00\x84\xC0\x74\x14\x0F\xB6\xCB\xE8\x16\x00\x00\x00\x84\xC0\x74\x08\xB0\x01\x48\x83\xC4\x20\x5B\xC3\x32\xC0\x48\x83\xC4\x20\x5B\xC3', 0))
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} C647055AC3 {mm.read(5).hex().upper()}', file=patches)

            # song limit
            mm.seek(mm.find(b'\x66\x39\x48\x08\x7F', 0) + 4)
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 9090 {mm.read(2).hex().upper()}', file=patches)

            mm.seek(mm.find(str.encode('music_data.bin'), 0) - 13)
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} {(str.encode(f"/datab/info/{ver}/music_bms.bin").hex().upper())} {mm.read(27).hex().upper()}', file=patches)

            mm.seek(mm.find(str.encode('class_course_data.bin'), 0) - 13)
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} {(str.encode(f"/datab/info/{ver}/class_course_bms.bin").hex().upper())} {mm.read(34).hex().upper()}', file=patches)

            mm.seek(mm.find(str.encode('/data/sound/')+(b'\x00'), 0))
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} {(str.encode(f"/datab/sound/").hex().upper())} {mm.read(13).hex().upper()}', file=patches)

            mm.seek(mm.find(str.encode('/data/movie/')+(b'\x00'), 0))
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} {(str.encode(f"/datab/movie/").hex().upper())} {mm.read(13).hex().upper()}', file=patches)

            print('# === BMS changes end ===', file=patches)

            pe.close()
            mm.close()

if __name__ == "__main__":
    game_version = int(input("Game version (ex: 28): "))
    create_patch("bm2dx.dll", f"iidx_bms_{game_version}.txt", game_version)
