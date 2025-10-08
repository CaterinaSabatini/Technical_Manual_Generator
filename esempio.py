from yt_dlp import YoutubeDL
import json
import re
import tempfile
import datetime
import base64
import io
import fotogrammi

#Keywords to be reviewed taking into account the sources found on Internet
KEYWORDS = [
    "teardown", "disassembly", "repair", "ifixit", "remove battery",
    "replace screen", "unscrew", "upgrade ram", "ssd removal",
    "keyboard removal", "motherboard", "step by step"
]

#Validation parameters for video selection

MIN_VIEWS = 10000
MIN_DURATION = 60 # seconds
MAX_DURATION = 3600 # 1h
MIN_LIKE_RATIO = 0.7 # min 70% likes vs total votes

#Create a temporary directory to store downloaded subtitles
dd = tempfile.TemporaryDirectory() 

#Path to the temporary directory
tempdir = dd.name

downloader = YoutubeDL({"skip_download": False,
                        "format": 'sb0',
                        "writeautomaticsub": True,
                        "outtmpl": {
                            "subtitle": f"{tempdir}/%(id)s",
                            "default": f"{tempdir}/%(id)s.mhtml"
                            }
                        })

data = downloader.extract_info("ytsearch1:macbook air 2012 repair")

with open(f"{tempdir}/data.json", "w") as f:
    json.dump(data, f)
with open(f"{tempdir}/{data['entries'][0]['id']}.en.vtt", 'r') as f:
    sottotitoli = f.readlines()

sottotitoli = sottotitoli[3:]
sottotitoli = [r for r in sottotitoli if not re.match("^\\s*\n", r)]
#sottotitoli = [r for r in sottotitoli if not re.match("^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}", r)]
sottotitoli = [re.sub("<[^>]*>","",r) for r in sottotitoli]
completi = []
prev = ''
time = None
for r in sottotitoli:
    if r != prev:
        if mm := re.match("^([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3})", r):
            time = datetime.datetime.strptime(mm.group(1) + '000', '%H:%M:%S.%f')
        else:
            completi.append({
                'tempo': time,
                'testo': r
                })
            prev = r
file_immagini = open(f"{tempdir}/{data['entries'][0]['id']}.mhtml", 'rb')
w = 0
h = 0
for ff in data['entries'][0]['formats']:
    if ff['format_id'] == "sb0":
        w = ff['width']
        h = ff['height']
immagini = fotogrammi.estrai_fotogrammi(file_immagini)
frames = []
for t,img in immagini:
    frames += fotogrammi.taglia_fotogramma(img, w, h, t['inizio'], t['fine'])

out = open("/tmp/file.html",'w')
out.write('<!DOCTYPE html>\n')
out.write('<html>\n')
out.write('<body>\n')
ccc = 0
par = False
while len(completi)>0 or len(frames)>0:
    if len(completi)>0 and (len(frames)==0 or completi[0]['tempo'] < frames[0][0]):
        if not par:
            out.write('<p>\n')
            par = True
        out.write(completi[0]['testo'])
        completi = completi[1:]
    else:
        if par:
            out.write('</p>\n')
            par = False
        datt = frames[0][1]
        datt.save(f"/tmp/immagine{ccc:02d}.png","PNG")
        ccc+=1
        buff = io.BytesIO()
        datt.save(buff, "PNG")
        buff.seek(0,0)
        datt = base64.b64encode(buff.read())
        out.write('<img src="data:image/png;base64, ' + datt.decode() + '" />\n')
        frames = frames[1:]
    if par:
        out.write('</p>\n')
        par = False
out.write('</body>\n')
out.write('</html>\n')
