from re import findall, search, compile
from xml.etree import ElementTree
from xml.dom.minidom import parseString
from time import sleep, time
from html import unescape
from urllib.request import urlopen,urlretrieve #,build_opener,HTTPCookieProcessor
from urllib.error import HTTPError
from http.cookiejar import CookieJar
from threading import Thread
from os.path import join, splitext, exists ,split
from os import mkdir

class BatchDownloader():
    def __init__(self, url, regex):
        # self._opener = build_opener()
        try:
            self._doc = urlopen(url).readall().decode(errors='ignore')
        except HTTPError as e:
            print('error code:%d, msg:%s' % (e.getcode(), e.msg))
        # try: #try simple xml tree parsing
        #     self._tree=ElementTree.fromstring(self._doc)
        # except ElementTree.ParseError as e:
        #     print('error line:%d, msg:%s' % (e.lineno, e.msg))
        # self._dom = parseString(self._doc)
        self._find = findall(regex, self._doc)
    def run(self,urlpre,fileUrlRE,downpath):
        if not exists(downpath): mkdir(downpath)
        # Thread(target=self._run,args=(urlpre,compile(fileUrlRE),compile(titleRE),downpath)).run()
        self._run(urlpre,compile(fileUrlRE),downpath)
    def _run(self,urlpre,fileUrlRE,downpath):
        log=open(join(downpath, 'fileList.txt'), 'a')
        for t,f,title in self._find:
            done=False
            furl,fname='',''
            while not done:
                try:
                    playerDoc = urlopen(urlpre.format(t) + f).readall().decode(errors='ignore')
                    furl = fileUrlRE.search(playerDoc).group()
                    title = unescape(title)
                     # title = unescape(titleRE.search(playerDoc).group().strip())
                    fname = title.replace('?','？').replace('<','[').replace('>',']').replace('*','.').replace('"',"'") + splitext(furl if not t=='v' else split(furl)[0])[1]
                    for c in '\\/:*?"<>|': fname = fname.replace(c,'') # replace characters that are not applicable for file name # possible future replacement = '__;_!\'()l'
                    fpath = join(downpath, fname)
                    if exists(fpath):
                        done=None
                    else:
                        if t=='a':
                            urlretrieve(furl, fpath)
                        elif t=='v':
                            urlretrieve(furl, 'tmp')
                            furl = split(furl)[0]
                            indexFname=''
                            with open('tmp') as f:
                                line=''
                                while not line.startswith('index'): line = f.readline()
                                indexFname=line
                            urlretrieve('/'.join((furl,indexFname)), 'tmp')
                            segments=[]
                            with open('tmp') as f:
                                line=' '
                                while line != '':
                                    line = f.readline()
                                    if line.startswith('segment'): segments.append(line)
                                indexFname=line
                            for segment in segments:
                                urlretrieve('/'.join((furl,segment)), 'tmp')
                                with open('tmp','rb') as f, open(fpath,'ab') as w:
                                    tmp=b' '
                                    while tmp != b'':
                                        tmp = f.read(1)
                                        w.write(tmp)
                    done=True
                except HTTPError as e:
                    print(e.code, e.msg)
                    sleep(3)
            print(furl, '=',title,'saved as' if done is True else 'already exists as', fname)
            if done is True: log.write(furl+'\t'+title+'\t\t\t\t'+fname+'\n')
        log.close()

if __name__ == '__main__':
    from sys import argv
    channel, workdir = '', ''
    if len(argv) == 3:
        channel, workdir = argv[1:3]
    elif len(argv) == 2:
        channel = argv[1]
    else:
        channel = input('channel name >')
    while not exists(workdir): workdir = input('existing work path ("." for current dir)>')

    BatchDownloader('http://%s.iblug.com/index.jsp?limit_num=999999999' % channel, '(?<=(?:jpg|png)"  onClick="fn_listen\(\'/podcast/(?P<type>[av])player_jw.jsp\?lecture_cd=)(?P<code>[^\'"&]+)(?:.{20,50}title=\')(?P<title>[^\']+)') \
        .run('http://%s.iblug.com/podcast/{}player_jw.jsp?lecture_cd=' % channel, '(?<=file: \')[^\']+', join(workdir,channel))