import os
import sys
import textwrap
import re
import tempfile
import tarfile
import time

class Ar:

    ar_file = None
    
    def __init__(self, filename=None, fileobj=None):
        if fileobj is not None:
            if filename is not None:
                raise Exception(
                    "Only one of filename and fileobj can be provided");
            self.ar_file = fileobj
        elif filename is not None:
            self.ar_file = open(filename,"wb")
        else:
            raise Exception("One of filename and fileobj must be provided");
        
        # write magic bytes
        self.ar_file.write("!<arch>\n")
        
        
    def add(self, filename, srcfilename=None, srccontents=None, srcfileobj=None):
        
        if srcfilename != None:
            f = open(srcfilename,"rb")
            srccontents = f.read()
            f.close()
        
        if srcfileobj != None:
            srccontents = srcfileobj.read()


        size = len(srccontents)
        modified = 0
        uid = 0
        gid = 0
        mode = 0644
        
        self.ar_file.write("%-16s" % filename)
        self.ar_file.write("%12d" % modified)
        self.ar_file.write("%6d" % uid)
        self.ar_file.write("%6d" % gid)
        self.ar_file.write("%8o" % mode)
        self.ar_file.write("%10d" % size)

        # ar header magic bytes (0x60 0x0A)
        self.ar_file.write("`\n")
        
        self.ar_file.write(srccontents)
        
        if size % 2 == 1:
            self.ar_file.write("\n")


    def close(self):
        self.ar_file.close()
        self.ar_file = None



class TarFileContext:
    tar = None
    mode = 0644
    uname = "root"
    gname = "root"
    
    def __init__(self, tar):
        self.tar = tar
    
    def usedefaults(self, info, mode, uname, gname):
        if mode is None:
            mode = self.mode
        if uname is None:
            uname = self.uname
        if gname is None:
            gname = self.gname
        
        info.mode = mode
        info.uname = uname
        info.gname = gname
    
    def adddir(self, alias, mode=None, uname=None, gname=None):
        info = tarfile.TarInfo()
        self.usedefaults(info, mode, uname, gname)
        info.type = tarfile.DIRTYPE
        info.name = alias
        self.tar.addfile(info)

    def addfile(self, file, alias, mode=None, uname=None, gname=None):
        f = open(file,"rb")
        info = self.tar.gettarinfo(fileobj=f)
        self.usedefaults(info, mode, uname, gname)
        info.name = alias
        self.tar.addfile(info,f)
        f.close()



class Deb:

    filename = None
    path = None
    release = "~"+time.strftime("%Y%m%d%H%M%S")
    extension = "deb"
    
    package = "test-package"
    version = "0.1"
    section = "base"
    priority = "optional"
    architecture = "all"
    depends = []
    maintainer = ""
    description = ""
    
    
    adddatafn = None
    

    #def __init__(self):
            

    

    def write_control(self, fileobj):
    
        def wrap_line(first,text):
            if first:
              initial_indent = ""
            else:
              initial_indent = " "
            wrapper = textwrap.TextWrapper(initial_indent=initial_indent,subsequent_indent=" ")
            result = []
            for line in wrapper.wrap(text):
                result.append(line)

            return "\n".join(result)
            
        def wrap_text(title, text):
            alltext = ": ".join([title,text])
            result = []
            first = True
            for line in alltext.split("\n"):
                line = wrap_line(first,line)
                if re.match("\s*$", line):
                    line = " ."
                result.append(line)
                first = False
            
            return "\n".join(result)
                    

        result = []            
        
        formatted_depends = wrap_text("Depends", ", ".join(self.depends))
        formatted_description = wrap_text("Description", self.description)
        
        fileobj.write("Package: %s\n" % self.package)
        fileobj.write("Version: %s%s\n" % (self.version, self.release) )
        fileobj.write("Maintainer: %s\n" % self.maintainer)
        fileobj.write("Section: %s\n" % self.section)
        fileobj.write("Priority: %s\n" % self.priority)
        fileobj.write("Architecture: %s\n" % self.architecture)
        fileobj.write(formatted_depends)
        fileobj.write("\n")
        fileobj.write(formatted_description)
        fileobj.write("\n")
        
    def addcontrolentries(self, controltar):

        f = tempfile.TemporaryFile()
        self.write_control(f)
        f.flush()
        f.seek(0)
        info = controltar.gettarinfo(arcname="control",fileobj=f)
        controltar.addfile(info,f)
        f.close()

    def adddataentries(self, datatar):
        if self.adddatafn is not None:
            self.adddatafn(datatar)

    def write(self):

        if self.filename is None:
            self.filename = self.package+"_"+self.version+self.release+"_"+self.architecture+"."+self.extension


        ar = Ar(self.path+"/"+self.filename)
        ar.add("debian-binary",srccontents="2.0\n")


        controltmpfile = tempfile.NamedTemporaryFile(prefix="control.tar.gz", delete=False)
        controltmpfile.close()
        control = tarfile.open(controltmpfile.name,mode="w:gz")
        
        self.addcontrolentries(control)
        control.close()
        
        ar.add("control.tar.gz",srcfilename=controltmpfile.name)
        os.remove(controltmpfile.name)


        datatmpfile = tempfile.NamedTemporaryFile(prefix="data.tar.gz", delete=False)
        datatmpfile.close()
        data = tarfile.open(datatmpfile.name,mode="w:gz")
        
        self.adddataentries(data)
        data.close()
        
        ar.add("data.tar.gz",srcfilename=datatmpfile.name)
        os.remove(datatmpfile.name)
        
        ar.close()
