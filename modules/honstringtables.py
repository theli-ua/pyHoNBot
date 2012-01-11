import xml.etree.ElementTree as etree
import re,zipfile,web
import StringIO
from os.path import basename

stringtablefiles = [ 'game/resources0.s2z/stringtables/entities_en.str' ]
re_entry = re.compile(r'(.+?)[\t\ ]+(.+)')
re_hero_name = re.compile(r'(Hero_[a-zA-z]+)_name')

def getVerInfo(os,arch,masterserver):
    details = urlencode().encode('utf8')
    url = Request('http://{0}/patcher/patcher.php'.format(masterserver),details)
    url.add_header("User-Agent",USER_AGENT)
    data = urlopen(url).read().decode("utf8", 'ignore')
    d = unserialize(data)
    return d

def setup(bot):
    if not hasattr(bot,'stringtables'):
        bot.stringtable_version = None

    verinfo = bot.masterserver_request({'version' : '0.0.0.0', 'os' : 'lac' ,'arch' : 'x86-biarch'},path = 'patcher/patcher.php')
    verinfo = verinfo[0]
    if bot.stringtable_version == verinfo['version']:
        print("no need to update stringtables")
        return


    manifest = None
    try:
        manifest = web.get('{0}{1}/{2}/{3}/manifest.xml.zip'.format(verinfo['url'],verinfo['os'],verinfo['arch'],verinfo['version']))
    except:pass
    if manifest is None:
        try:
            manifest = web.get('{0}{1}/{2}/{3}/manifest.xml.zip'.format(verinfo['url2'],verinfo['os'],verinfo['arch'],verinfo['version']))
        except:pass
    if manifest is None:
        print("Couldn't get manifest for hon's files")
        return
    
    bot.stringtables = {}
    bot.heroshorts = {}
    manifest = etree.fromstring(zipfile.ZipFile(StringIO.StringIO(manifest)).read('manifest.xml'))
    files = []
    for e in manifest:
        if e.tag == 'file' and e.attrib['path'] in stringtablefiles:
            files.append(e.attrib)
    for f in files:
        if f['version'].count('.') == 3 and f['version'].endswith('.0'):
            f['version'] = f['version'][:-2]
        table = None
        try:
            table = web.get('{0}{1}/{2}/{3}/{4}.zip'.format(verinfo['url'],verinfo['os'],verinfo['arch'],f['version'],f['path']))
        except:pass
        if table is None:
            try:
                table = web.get('{0}{1}/{2}/{3}/{4}.zip'.format(verinfo['url2'],verinfo['os'],verinfo['arch'],f['version'],f['path']))
            except:pass
        if table is None:
            print("Wasn't able to fetch {0}".format(f['path']))
            continue
        table = zipfile.ZipFile(StringIO.StringIO(table)).read(basename(f['path']))
        try:
            table = table.decode("utf8")
        except:
            table = table.decode("cp1251")
        table = table.splitlines()
        for line in table:
            m = re_entry.match(line)
            if m:
                bot.stringtables[m.group(1)] = m.group(2)
                m2 = re_hero_name.match(m.group(1))
                if m2:
                    short = m.group(2).lower()
                    if short.startswith('the '):
                        short = short[4:]
                    short = short[:4].strip()
                    if short not in bot.heroshorts:
                        bot.heroshorts[short] = m2.group(1)
                    else:
                        old = bot.heroshorts[short]
                        longer_old = bot.stringtables[bot.heroshorts[short] + '_name'][4:].strip().lower()
                        longer_new = m.group(2).lower()[4:].strip()
                        del bot.heroshorts[short]
                        short_old = short
                        short_new = short
                        i = 0
                        while short_old == short_new:
                            if i < len(longer_old):
                                short_old += longer_old[i]
                            if i < len(longer_new):
                                short_new += longer_new[i]
                            i+=1
                        bot.heroshorts[short_old] = old
                        bot.heroshorts[short_new] = m2.group(1)

    bot.stringtable_version = verinfo['version']
    
