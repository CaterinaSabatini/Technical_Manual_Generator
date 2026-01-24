from bs4 import BeautifulSoup
from PIL import Image
import datetime
import io

"""
 Functions to extract frames from mhtml data

 @param data: binary data of the mhtml file
 @return: list of tuples (time, image data)
"""
def headers(data):
    head = {}
    row, rest = data.split(b'\r\n',1)
    while len(row) > 0:
        name, value = row.split(b': ', 1)
        head[name.upper()] = value
        row, rest = rest.split(b'\r\n',1)
    return (head, rest)

"""
Extract frames from mhtml data

@param data: binary data of the mhtml file
@return: list of tuples (time, image data)
"""
def extract_frames(data):
    header, rest = headers(data)
    bound = header[b"CONTENT-TYPE"].split(b'boundary="')[1].split(b'"')[0]

    rest = rest.split(b"\r\n",1)[1]
    chunks = rest.split(b"\r\n--" + bound + b"--\r\n")[0].split(b"\r\n--" + bound + b"\r\n")

    limg = chunks[0]
    head, cont = headers(limg)
    soup = BeautifulSoup(cont, "html.parser")

    res = soup.find_all("figcaption")
    
    #Extract time intervals from captions
    text = [x.string for x in res]
    text = [x.split(': ',1)[1] for x in text]
    text = [{'start': x.split(" – ",1)[0], 'end': x.split(" – ",1)[1].split(' ')[0]} for x in text]
    text = [{'start': datetime.datetime.strptime(x['start'] + '000', "%H:%M:%S,%f"),'end': datetime.datetime.strptime(x['end'] + '000', "%H:%M:%S,%f")} for x in text]

    return [(t, headers(c)[1]) for c,t in zip(chunks[1:], text)]

"""
Crop frames into smaller images

@param dat: binary data of the image
@param w: width of each cropped image
@param h: height of each cropped image
@param start: start time of the frame
@param end: end time of the frame
@return: list of tuples (time, cropped image)
"""
def crop_frames(dat, w,h, start, end):
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
            results.append((start + (cont*(end-start)/cmax), img.crop((x,y,x+w,y+h))))
            x += w
            cont += 1
        y += h
    return results

