from pathlib import Path

import lxml.etree as ET
#import glob
import json
import shutil

import ifstools
import mem_patch_bm3
import musicdata_tool


output = 'output'

missing = []
for file in ['bm2dx.dll', 'mselect.ifs', 'music_bm3.json', 'music_bm3_merge.json', 'tex_bm3', output]:
    if not Path(file).exists():
        missing.append(file)
if missing:
    raise SystemExit('MISSING REQUIRED FILES:\n' + '\n'.join(map(str, missing)))

game_version = int(input('Game version (ex: 28): '))

ver = '0' if game_version % 2 == 0 else '1'

mem_patch_bm3.create_patch('bm2dx.dll', Path(output, f'iidx_bm3_{game_version}.txt'), game_version)
Path('bm2dx.dll').unlink()

with open('music_bm3.json', 'r', encoding='utf-8') as file:
    music_bm3 = json.load(file)
music_bm3.update({'data_ver': game_version})
json.dump(music_bm3, open('music_bm3.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
musicdata_tool.create_file('music_bm3.json', Path(output, 'data', 'info', ver, 'music_bm3.bin'), game_version)


with open('music_bm3_merge.json', 'r', encoding='utf-8') as file:
    music_bm3 = json.load(file)
music_bm3.update({'data_ver': game_version})
json.dump(music_bm3, open('music_bm3_merge.json', 'w', encoding='utf8'), indent=4, ensure_ascii=False)
musicdata_tool.create_file('music_bm3_merge.json', 'music_bm3_merge.bin', game_version)
musicdata_tool.merge_files('music_bm3_merge.bin', Path(output, 'data', 'info', ver, 'music_omni.bin'), Path(output, 'data', 'info', ver, 'music_bmni.bin'))
Path('music_bm3_merge.bin').unlink()

#for folders in glob.glob(f'output/data/sound/*'):
#    mid = int(Path(folders).name)
#    if mid < 3000:
#        new_id = mid + 50
#    
#    if mid >= 3000:
#        new_id = mid + 300
#
#    for file in glob.glob(f'{folders}/*'):
#        Path('out', 'data', 'sound', f'0{new_id}').mkdir(parents=True, exist_ok=True)
#        shutil.copy(file, Path('out', 'data', 'sound', f'0{new_id}', f'0{new_id}{Path(file).name[5:]}'))

def extract_ifs(file):
    ifs = ifstools.IFS(file)
    ifs.extract(progress=True, recurse=False, path="mselect")
    ifs.close()

extract_ifs('mselect.ifs')

shutil.copytree('tex_bm3', Path('mselect', 'tex'), dirs_exist_ok=True)

parser = ET.XMLParser(remove_blank_text=True)

tree = ET.parse(str(Path('mselect', 'tex', 'texturelist.xml')), parser)
root = tree.getroot()

count = 0
for texture_list in root:
    for texture in texture_list:
        if texture.get('name') in ['so_6th', 'so_5th', 'so_4th', 'so_3rd', 'so_2nd', 'so_1st', 'so_sub']:
            texture.getparent().remove(texture)
    count += 1

texture = ET.SubElement(root, 'texture')
texture.set('format', 'argb8888rev')
texture.set('mag_filter', 'nearest')
texture.set('min_filter', 'nearest')
texture.set('name', f'tex0{count}')
texture.set('wrap_s', 'clamp')
texture.set('wrap_t', 'clamp')
size = ET.SubElement(texture, 'size')
size.text = '1024 1024'
size.set('__type', '2u16')

values = [
    ['so_1st', '2 624 2 74', '0 626 0 76'],
    ['so_2nd', '628 1250 2 74', '626 1252 0 76'],
    ['so_3rd', '1254 1876 2 74', '1252 1878 0 76'],
    ['so_4th', '2 624 78 150', '0 626 76 152'],
    ['so_5th', '628 1250 78 150', '626 1252 76 152'],
    ['so_6th', '1254 1876 78 150', '1252 1878 76 152'],
    ['so_sub', '2 624 154 226', '0 626 152 228']
]

for so in values:
    img = ET.SubElement(texture, 'image')
    img.set('name', so[0])
    uv = ET.SubElement(img, 'uvrect')
    uv.text = so[1]
    uv.set('__type', '4u16')
    im = ET.SubElement(img, 'imgrect')
    im.text = so[2]
    im.set('__type', '4u16')

tree.write(str(Path('mselect', 'tex', 'texturelist.xml')), encoding='utf-8', xml_declaration=True, pretty_print=True)

ifstools.IFS('mselect').repack(progress=True, use_cache=True, path=Path(output, 'data', 'graphic', ver, 'mbelect.ifs'))

shutil.rmtree('mselect')
Path('mselect.ifs').unlink()
