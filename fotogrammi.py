from bs4 import BeautifulSoup
from PIL import Image
import datetime
import io

def headers(data):
    head = {}
    row, rest = data.split(b'\r\n',1)
    while len(row) > 0:
        name, value = row.split(b': ', 1)
        head[name.upper()] = value
        row, rest = rest.split(b'\r\n',1)
    return (head, rest)

def estrai_fotogrammi(file):

    while (r := file.readline()) != b'\r\n':
        if r.startswith(b"Content-type:"):
            bound = r.split(b'boundary="')[1].split(b'"')[0]

    sep = file.readline()
    if sep != (b"--" + bound + b"\r\n"):
        print("errore: separatore sbagliato")
        exit(1)

    content = file.read()

    chunks = content.split(b"\r\n--" + bound + b"--\r\n")[0].split(b"\r\n--" + bound + b"\r\n")

    limg = chunks[0]
    head, cont = headers(limg)
    soup = BeautifulSoup(cont, "html.parser")

    res = soup.find_all("figcaption")
    testi = [x.string for x in res]
    testi = [x.split(': ',1)[1] for x in testi]
    testi = [{'inizio': x.split(" – ",1)[0], 'fine': x.split(" – ",1)[1].split(' ')[0]} for x in testi]
    testi = [{'inizio': datetime.datetime.strptime(x['inizio'] + '000', "%H:%M:%S,%f"),'fine': datetime.datetime.strptime(x['fine'] + '000', "%H:%M:%S,%f")} for x in testi]

    return [(t, headers(c)[1]) for c,t in zip(chunks[1:], testi)]

def taglia_fotogramma(dat, w,h, inizio, fine):
    data_file = io.BytesIO(dat)
    img = Image.open(data_file)
    tw, th = img.width, img.height
    x = 0
    y = 0
    results = []
    cont = 0
    cmax = (tw//w)*(th//h)
    while y+h <= th:
        x = 0
        while x+w <= tw:
            results.append((inizio + (cont*(fine-inizio)/cmax), img.crop((x,y,x+w,y+h))))
            x += w
            cont += 1
        y += h
    return results

