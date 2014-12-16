from re import findall, search, compile
from xml.etree import ElementTree
from xml.dom.minidom import parseString
from time import sleep, time
from html import unescape
from urllib.request import urlopen,urlretrieve #,build_opener,HTTPCookieProcessor
from urllib.error import HTTPError
from http.cookiejar import CookieJar
from threading import Thread
from os.path import join, splitext, exists

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
    def run(self,urlpre,re,fre,downpath):
        # Thread(target=self._run,args=(urlpre,compile(re),compile(fre),downpath)).run()
        self._run(urlpre,compile(re),compile(fre),downpath)
    def _run(self,urlpre,re,fre,downpath):
        log=open(join(downpath, 'fileList.txt'),'w')
        for f in self._find:
            done=False
            furl,title,fname='','',''
            while not done:
                try:
                    playerDoc = urlopen(urlpre + f).readall().decode(errors='ignore')
                    furl = re.search(playerDoc).group()
                    title = fre.search(playerDoc).group().strip().unescape()
                    fname = title.replace('?','？').replace('<','[').replace('>',']').replace('*','.').replace('"',"'") + splitext(furl)[1]
                    for c in '\\/:*?"<>|': fname = fname.replace(c,'') # replace characters that are not applicable for file name # possible future replacement = '__;_!\'()l'
                    fpath=join(downpath, fname)
                    if not exists(fpath):
                        urlretrieve(furl, fpath)
                    done=True
                except HTTPError as e:
                    print(e.code, e.msg)
                    sleep(3)
            print(furl, '=',title,'saved as', fname)
            log.write(furl+'\t'+title+'\t\t\t\t'+fname+'\n')
        log.close()

if __name__ == '__main__':
    channel='sciencewithpeople'#'birdfly'
    BatchDownloader('http://%s.iblug.com/index.jsp?limit_num=999999999' % channel, '(?<=png"  onClick="fn_listen\(\'/podcast/aplayer_jw.jsp\?lecture_cd=)[^\'"&]+') \
        .run('http://%s.iblug.com/podcast/aplayer_jw.jsp?lecture_cd=' % channel, '(?<=file: \')[^\']+', '(?<=class="title">)[^<]+', 'E:\\iblug_backup\\%s' % channel)
