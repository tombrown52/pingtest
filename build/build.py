import os
import debutils
import tarfile

def main():
    deb = debutils.Deb()
    
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    deb.path = "../dist"
    
    deb.package = "pingtest"
    deb.version = "1.0"
    deb.depends = [ ]
    deb.maintainer = "Tom Brown <tombrown52@gmail.com>"
    deb.description = """
        Continuously pings the loopback address and logs the timed results to help identify system pauses
    """
    deb.adddatafn = adddatafn
    deb.release = ""
    
    if not os.path.exists(deb.path):
        os.makedirs(deb.path)
    
    deb.write()
    
    print "Completed building package: "+deb.filename

def adddatafn(tar):

    context = debutils.TarFileContext(tar)
    context.uname = "root"
    context.mode = 0644

    context.adddir("etc/init")
    context.adddir("etc/lograte.d")
    
    context.addfile("../src/etc/init/pingtest.conf",   "etc/init/pingtest.conf")
    context.addfile("../src/etc/logrotate.d/pingtest", "etc/logrotate.d/pingtest")

if __name__ == "__main__":
    main()
