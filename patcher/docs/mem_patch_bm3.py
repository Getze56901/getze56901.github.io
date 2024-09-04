import mmap
import pefile

def create_patch(infile, outfile, game_version):

    with open(infile, 'r+b') as bm2dx:
        with open(outfile, 'w', newline='\r\n') as patches:
            mm = mmap.mmap(bm2dx.fileno(), 0)
            pe = pefile.PE(infile, fast_load=True)

            ver = '0' if game_version % 2 == 0 else '1'

            print('# === Omnimix + beatmania III changes. ===', file=patches)

            #X rev
            mm.seek(mm.find(b'\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x40\x53\x48\x83\xEC\x20\x0F\xB6\xD9\xE8\x22\x01\x00\x00\x84\xC0\x74\x14\x0F\xB6\xCB\xE8\x16\x00\x00\x00\x84\xC0\x74\x08\xB0\x01\x48\x83\xC4\x20\x5B\xC3\x32\xC0\x48\x83\xC4\x20\x5B\xC3', 0))
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} C6470558C3 {mm.read(5).hex().upper()}', file=patches)
            print("## F rev instead of X rev (uncomment with music_bm3.bin below)", file=patches)
            print(f'#bm2dx.dll {hex(offset)[2:].upper()} C6470546C3 C6470558C3', file=patches)

            #song limit
            mm.seek(mm.find(b'\x66\x39\x48\x08\x7F', 0) + 4)
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 9090 {mm.read(2).hex().upper()}', file=patches)

            #mdato.ifs
            mm.seek(mm.find(str.encode('mdata.ifs'), 0) + 4)
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 6F {mm.read(1).hex().upper()}', file=patches)

            #mbelect.ifs
            mm.seek(mm.find(str.encode('mselect.ifs'), 0) + 1)
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 62 {mm.read(1).hex().upper()}', file=patches)

            #music_omni.bin
            mm.seek(mm.find(str.encode('music_data.bin'), 0) + 6)
            offset = pe.get_rva_from_offset(mm.tell())
            print(f'bm2dx.dll {hex(offset)[2:].upper()} 626D6E69 {mm.read(4).hex().upper()}', file=patches)
            #music_diff.bin
            print("## music_diff.bin (uncomment for omni songs only)", file=patches)
            print(f'#bm2dx.dll {hex(offset)[2:].upper()} 64696666 626D6E69', file=patches)
            #music_bm3.bin
            print("## music_bm3.bin (uncomment for BM3 songs only)", file=patches)
            print(f'#bm2dx.dll {hex(offset)[2:].upper()} 626D332E62696E00 626D6E692E62696E', file=patches)

            #music_title_omni.xml
            mm.seek(mm.find(str.encode('music_title_yomi.xml'), 0) + 12)
            if mm.tell() > 0x1000:
                print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 6F6D6E69 {mm.read(4).hex().upper()}', file=patches)

            #music_artist_omni.xml
            mm.seek(mm.find(str.encode('music_artist_yomi.xml'), 0) + 13)
            if mm.tell() > 0x1000:
                print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 6F6D6E69 {mm.read(4).hex().upper()}', file=patches)

            #video_music_omni.xml
            mm.seek(mm.find(str.encode('video_music_list.xml'), 0) + 12)
            if mm.tell() > 0x1000:
                print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} 6F6D6E69 {mm.read(4).hex().upper()}', file=patches)

            #omni songs in legg folder
            mm.seek(mm.find(b'\x7C\xED\x32\xC0\xC3', 0) + 2)
            print(f'bm2dx.dll {hex(pe.get_rva_from_offset(mm.tell()))[2:].upper()} B001 {mm.read(2).hex().upper()}', file=patches)

            print('# === Omnimix + beatmania III changes end ===', file=patches)

            pe.close()
            mm.close()

if __name__ == "__main__":
    game_version = int(input("Game version (ex: 28): "))
    create_patch("bm2dx.dll", f"iidx_bm3_{game_version}.txt", game_version)
