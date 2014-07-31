from bs4 import BeautifulSoup
import requests
import mechanize
import time
import logging
import logging.handlers
import threading
import sys
import traceback


logger = logging.getLogger('Alexa')
debug_level = True
# debug_level = False

url_pattern = {
               'global': "http://www.alexa.com/topsites/global;%s",
               'jp':"http://www.alexa.com/topsites/countries;%s/JP",
               'au':"http://www.alexa.com/topsites/countries;%s/AU",
               'us':"http://www.alexa.com/topsites/countries;%s/US",
}

headers = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}
               
proxies = {
          "http": "http://10.64.8.8:8080",
          "ftp": "http://10.64.8.8:8080",
}

ib_tky_proxies = {
        "http": "http://proxy-tky.ib.tmicss.com:8080"
}

ib_proxies = {
          "http": "http://10.64.1.125:8080"
}


iwsaas_proxies = {
          "http": "http://proxy.iws.trendmicro.com",
          "ftp": "http://proxy.iws.trendmicro.com",
}


'''
<li class="site-listing">
<div class="count">4</div>
<div class="desc-container">
<p class="desc-paragraph">
<a href="/siteinfo/yahoo.com">Yahoo.com</a>
</p>
<span class="small topsites-label"></span>
<div class="description">A major internet portal and service provider offering search results, customizable content, cha<span class='truncate'>... <a class='moreDesc'>More</a></span><span class="remainder">trooms, free e-mail, clubs, and pager.</span></div>
</div>
'''


class AlexaSpider(object):      

    def __init__(self):
        print "Init..."
        pass
    
    def __is_url_wanted(self, tag):
        return tag.has_attr('class') and "site-listing" in tag['class']


    def __format_one_site(self, li):
        return "%s: %s" % (li.div.string, li.p.a.string)
    
    def pageNo(self, page, region='global'):  
        # print "process page %s..." % page     
        r = requests.get(url_pattern[region] % (page), proxies=proxies, headers=headers)
        data = r.text
        
        soup = BeautifulSoup(data)
        for link in soup.find_all(self.__is_url_wanted):
            print(self.__format_one_site(link))
    
    def topN(self, region='global', top=100, start=0):
        max_page = top / 25
        start_page = start / 25
        for i in xrange(max_page):
            if i < start_page:
                continue
            self.pageNo(i, region)
            time.sleep(1)
        




class Verifier(object):
    
    def __init__(self, proxy=None, username=None, password=None):
        self.proxy = proxy
        self.br = mechanize.Browser()
        self.username = username
        self.password = password
        self.first_url = 'http://www.baidu.com'
    
    def run_with_mechanize(self, url_list):
        self.br = mechanize.Browser()
        self.br.set_handle_equiv(True)
        #br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
          
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
  
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36')]
        
        if self.proxy is not None:
            br = self.br
            try:
                self.br.set_proxies(self.proxy)
                r = self.br.open(self.first_url)
                self.br._factory.is_html = True
                logger.debug("url: %s", r.geturl())
                
                for f in self.br.forms():
                    logger.debug(f)
                
                self.br.select_form(nr=0)
                self.br.form['username'] = username
                r = self.br.submit()
                if r.code != 200:
                    logger.error("Error when input username: %s", r.code)
                    
                self.br._factory.is_html = True
                logger.debug("url: %s", r.geturl())
                for f in self.br.forms():
                    logger.debug(f)
                           
                #print "after input username"
                self.br.select_form(nr=0)
                self.br.form['password'] = password
                r = self.br.submit()
                if r.code != 200:
                    logger.error("Error when input password: %s", r.code)
                    
                self.br._factory.is_html = True
                
                #print "after input password"
                
                logger.debug("url: %s", r.geturl())
                logger.debug("header: %s", r.info())
                logger.debug("response code: %s", r.code)
                logger.debug("Authentication is done via %s", first_url)
                #print first_url, r.code, len(r.read()), self.br.title()
                #return self.url, r.code, len(r.read()), self.br.title()
            except mechanize.HTTPError as e:
                logger.debug("HTTP Error status code: %s", e.code)
                logger.debug("HTTP Error title:%s", self.br.title())
                #return self.url, e.code, len(r.read()),self.br.title()
            except mechanize.URLError as e:
                logger.debug("URLError: %s", e.reason.args)
                #return self.url, e.reason.args, len(r.read()), self.br.title()
            except Exception as e:
                logger.debug("Other Error: %s", e)
                

        # now auth is ready, continue to do the real stuff
        for url in url_list:
            try: 
                response = self.br.open(url)
                logger.info("%s: %d -> %s", url, r.code, self.br.title())
                logger.debug("title: %s", self.br.title())
                #return self.url, response.code, len(response.read()), br.title() 
                print "%s: %d -> %s" % (url, r.code, self.br.title())
            except mechanize.HTTPError as e:
                logger.debug("HTTP Error status code: %s", e.code)
                logger.debug("HTTP Error title:%s", self.br.title())
                print "%s: %d -> %s" % (url, e.code, self.br.title())
                #return self.url, e.code, len(r.read()),self.br.title()
            except mechanize.URLError as e:
                logger.debug("URLError: %s", e.reason.args)
                print "%s: %d -> %s" % (url, e.reason.args, self.br.title())
                #return self.url, e.reason.args, len(r.read()), self.br.title()
            except Exception as e:
                print "%s: err -> %s" % (url, e)
                logger.debug("Other Error: %s", e)
                
              
            
        
             
    def run_with_request(self):
        r = requests.get("http://%s" % self.url, proxies=proxies, headers=headers)
        data = r.text
        print len(data)
        
    def test(self):
        s = requests.Session()       
        r = s.get('http://httpbin.org/cookies/set/sessioncookie/123456789', proxies=iwsaas_proxies, headers=headers)
        print(r.text)
#         r = s.get("http://httpbin.org/cookies")
 

      
'''
class Alaska(Object):
    def __init__(self, proxy=None):
        self.br = mechanize.Browser()
        self.proxy = proxy
        self.is_authenticated = False


    def go(self, url_list):
        for url in url_list:
            try:
                response = self.br.open(url)
            except Exception, e:
                logger.error("%s: %s", url, e)
                print("%s: %s", url, e)

    def auth(self, username, password, ever_first_url='http://www.baidu.com'):
        # authenticate the user firstly.
        if self.proxy is not None:
            br = self.br
            try:
                response = br.open(ever_first_url)
                # input username

                br.set_proxies(self.proxy)
                r = br.open(self.url)
                br._factory.is_html = True
                logger.debug("url: %s", r.geturl())
                
                for f in br.forms():
                    logger.debug(f)
                
                br.select_form(nr=0)
                br.form['username'] = username
                r = br.submit()
                if r.code != 200:
                    logger.error("Error when input username: %s", r.code)
                    
                br._factory.is_html = True
                logger.debug("url: %s", r.geturl())
                for f in br.forms():
                    logger.debug(f)
                           
                print "after input username"
                br.select_form(nr=0)
                br.form['password'] = password
                r = br.submit()
                if r.code != 200:
                    logger.error("Error when input password: %s", r.code)
                    
                br._factory.is_html = True
                
                print "after input password"
                
                logger.debug("url: %s", r.geturl())
                logger.debug("header: %s", r.info())
                logger.debug("response code: %s", r.code)
                print self.url, r.code, len(r.read()), br.title()
                
                self.is_authenticated = True
                return self.url, r.code, len(r.read()), br.title()
            except mechanize.HTTPError as e:
                logger.debug("HTTP Error status code: %s", e.code)
                logger.debug("HTTP Error title:%s", br.title())
                return self.url, e.code, len(r.read()),br.title()
            except mechanize.URLError as e:
                logger.debug("URLError: %s", e.reason.args)
                return self.url, e.reason.args, len(r.read()), br.title()
        else:
            self.is_authenticated = True
'''

def get_top_site_list():
    w = AlexaSpider()
    # w.pageN(6)
    # w.topN(500)
    # w.topN(500,276)
    w.topN('us', 500)
    
def check_if_url_blocked(url_list, proxy, username, password):
    # v = Verifier('www.stackoverflow.com')
    v = Verifier(proxy, username, password)       
    v.run_with_mechanize(url_list)

    '''
    try:
        m = v.run_with_mechanize(iwsaas_proxies, username, password)
        n = v.run_with_mechanize()
        logger.info(n)
        logger.info(m)

        if m[-1] == n[-1]:
            print "%s: PASS <%s..%s> (%d .vs. %d)" % (url, m[1], n[1], m[-2], n[-2])
            logger.info("%s: PASS <%s..%s> (%d .vs. %d)", url, m[1], n[1], m[-2], n[-2])
        else:
            print "%s: FAIL <%s..%s> (%d .vs. %d)" % (url, m[1], n[1], m[-2], n[-2])
            logger.info("%s: FAIL <%s..%s> (%d .vs. %d)", url, m[1], n[1], m[-2], n[-2])
    except Exception, e:
            print "%s: ERR %s" % (url, e)
            logger.info("%s: ERR", url)
            logger.info("%s", e)
            raise e
            #logger.info("%s", traceback.format_exec())
    '''

def go(url_list, n, step, username, password):
    start = n*step
    stop = (n+1)*step 
    logger.info("checking url range: %d -> %d", start, stop)
    check_if_url_blocked(url_list[start:stop], iwsaas_proxies, username, password)


if __name__ == "__main__":
#     main()
    log_file = sys.argv[1] 
    url_file = sys.argv[2]
    total = int(sys.argv[3]) or 1
    step = int(sys.argv[4]) or 1
    username = sys.argv[5]
    password = sys.argv[6]
    formatter = logging.Formatter("%(asctime)s    %(levelname)s    %(filename)s    #%(lineno)d    <%(process)d:%(thread)d>    %(message)s")
    #handler = logging.handlers.TimedRotatingFileHandler(options.logfile, 'm', 1, 5)
    handler = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', 1, 5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    if debug_level:
        logger.setLevel(logging.DEBUG)

    #f = open('jp-all.txt')   
    f = open(url_file)   
    url_list = []
    for line in f.readlines():
        url = 'http://www.' + line.split(':')[-1].strip()
        url_list.append(url)
    
    print url_list

    threads = []
    for n in xrange(total/step):
        thread = threading.Thread(target=go, args=[url_list, n, step, username, password])
        thread.start()

        threads.append(thread) 
            

    for thread in threads:
        thread.join()

    print "DONE!"

