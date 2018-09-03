import requests
import os
import re
import json
from tqdm import tqdm
from time import sleep

url = "http://jwfw.fudan.edu.cn/eams/stdSyllabus!search.action"

sess = requests.Session()
sess.headers.update({
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"en-US,en;q=0.9",
    "Connection":"keep-alive",
    "Content-Length":"67",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie":"请使用你自己的cookie", # !!! modify here
    "Host":"jwfw.fudan.edu.cn",
    "Origin":"http://jwfw.fudan.edu.cn",
    "Referer":"http://jwfw.fudan.edu.cn/eams/stdSyllabus!search.action",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest"
})

def getInfo(pageNo):
    try:
        res = sess.post(url, data={
            "lesson.project.id":1,
            "lesson.semester.id":284, # !!! modify here
            "_":1517105070988,
            "pageNo":pageNo
        }).text
        return res
    except:
        sleep(2)
        return getInfo(pageNo)

ptr = re.compile('<tr>(.*?)<\/tr>', re.S)
plessonIds = re.compile('value="(\d+)"')
pnum = re.compile('>(\w*\d*\.\d*)<')
pname = re.compile('查看任务详细信息">(.*)<\/a>')
pcredit = re.compile('<\/a><\/td><td>(\d*)<\/td>')
ptutor = re.compile('<\/a><\/td><td>\d*<\/td><td>(.*?)<\/td>')
ptitle = re.compile('<\/a><\/td><td>\d*<\/td><td>.*?<\/td><td>(.*?)<')
plimit = re.compile('<\/a><\/td><td>\d*<\/td><td>.*?<\/td><td>.*?<\/td><td>(\d*)<\/td')
pplace = re.compile('"longTextFormat">(.*?)<', re.S)
ptiming = re.compile('"longTextFormat">.*?<\/td><td>(.*?)<\/td><td>', re.S)
pdepart = re.compile('"longTextFormat">.*?<\/td><td>.*?<\/td><td>(.*?)<', re.S)

def extract(text):
    def get(l):
        if len(l) > 0:
            return l[0]
        return ' '
    try:
        lessonIds = plessonIds.findall(text)[0]
        cid = lessonIds
        num = get(pnum.findall(text))
        name = get(pname.findall(text))
        credit = get(pcredit.findall(text))
        tutor = get(ptutor.findall(text))
        title = get(ptitle.findall(text))
        limit = get(plimit.findall(text))
        place = get(pplace.findall(text))
        timing = get(ptiming.findall(text))
        depart = get(pdepart.findall(text))
        return {lessonIds: {
            'cid': cid,
            'num': num,
            'name': name,
            'credit': credit,
            'tutor': tutor,
            'title': title,
            'limit': limit,
            'place': place,
            'timing': timing,
            'depart': depart
        }}

    except:
        return {}
    

errcnt = 0
def parse(text):
    global errcnt
    lines = ptr.findall(text)
    res = {}
    for line in lines:
        res.update(extract(line))
    if len(res) != len(lines) - 2:
        open('err' + str(errcnt) + '.html', 'w').write(text)
        errcnt = errcnt + 1
    return res

res = {}
for pageNo in tqdm(range(1, 152)): # !!! modify here
    res.update(parse(getInfo(pageNo)))

json.dump(res, open('courses.json', 'w'))
print("finished, totally {} course entry crawled!".format(len(res)))

