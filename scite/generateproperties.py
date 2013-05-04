
import os

g_pythonpath = r'c:\Python27\python.exe'
g_lnzpath = r'C:\Users\diamond\Documents\fisherapps\coding\lnzscript\lnzscript.exe'
assert os.path.exists(g_pythonpath)
assert os.path.exists(g_lnzpath)

class Bucket(): pass
Subsys = Bucket()
Subsys.exec_wait = 0 #(console) Command line programs. Do not use for GUI programs as their windows will not be visible.
Subsys.windows = 1 #Programs that create their own windows
Subsys.exec_async = 2 #(shell) A good way to open HTML files and similar as it handles this similarly to a user opening the file from the shell.
Subsys.script = 3 #
Subsys.htmlhelp = 4 # Open in HtmlHelp program
Subsys.winhelp = 5 #Open with WinHelp function

# a 'filter' modifies the current file 
#supported only on windows is command.quiet

# note: it might be possible to use this without a python extension, due to
# command.input.0.*.cc=$(CurrentSelection) or currentword and so on., replaceselection , etc
#~ ScApp.SetProperty('command.name.38.*', 'Python new')

class GenProperties():
    currentIndex = 30
    arLines = None
    def __init__(self): self.arLines = []; self.idmkeys=[]
    def reg(self, sShortcut, sName, sCommand, sFiletype='*', subsys=Subsys.exec_async, savebefore=False, n=None):
        i = n if n else self.currentIndex
        self.arLines.append('')
        self.arLines.append('command.name.%d.%s=%s'%(i, sFiletype,sName))
        self.arLines.append('command.subsystem.%d.%s=%d'%(i, sFiletype,subsys))
        if sShortcut:
            self.arLines.append('command.shortcut.%d.%s=%s'%(i, sFiletype,sShortcut))
        self.arLines.append('command.%d.%s=%s'%(i, sFiletype,sCommand))
        if not savebefore:
            self.arLines.append('command.mode.%d.%s=savebefore:no'%(i, sFiletype))
        
        if not n: self.currentIndex += 1
            
    def regidm(self, sShortcut, sCommand):
        assert not any(key[0]==sShortcut for key in self.idmkeys), 'already exists'
        self.idmkeys.append((sShortcut, sCommand))
    
    def regpy(self, sShortcut, sName, sCommand, sFiletype='*', subsys=Subsys.script, savebefore=False):
        if 'plugins.' in sCommand: sCommand = 'import plugins; '+sCommand
        return self.reg(sShortcut=sShortcut,sName=sName,sCommand=sCommand,sFiletype=sFiletype,
            subsys=subsys, savebefore=savebefore)
    def addraw(self, s):
        self.arLines.append('')
        self.arLines.append(s)
        
    def write(self):
        target = os.path.join('properties', 'pyplugin_generated.properties')
        f=open(target,'w')
        f.write('#Warning: this file is automatically generated\n')
        f.write('#Manual edits will be discarded\n')
        for line in self.arLines:
            print line.strip()
            f.write(line)
            f.write('\n')
        f.write('\nuser.shortcuts=\\\n')
        f.write('$(user.shortcuts)\\\n')
        for line in self.idmkeys:
            f.write(line[0]+'|'+line[1]+'|\\\n')
        f.close()

gen = GenProperties()
gen.currentIndex = 30
assert 'python.exe' in g_pythonpath
gen.addraw('pyplugin.pypath=%s'%g_pythonpath)
gen.addraw('pyplugin.pypathw=%s'%g_pythonpath.replace('python.exe','pythonw.exe'))
gen.addraw('pyplugin.lnzpath=%s'%g_lnzpath)

#basic overrides
gen.regidm('Ctrl+R','IDM_WRAP')
gen.regidm('Ctrl+Alt+Shift+R','IDM_REVERT')
gen.regidm('Ctrl+;','IDM_OPENGLOBALPROPERTIES')
gen.regidm('Ctrl+Shift+X','2337') #linecut
gen.regidm('Ctrl+L','2338') #linedelete (delete instead of cut)
gen.regidm('Ctrl+Alt+F4','IDM_CLOSEALL')

# go 'back' and 'forward' to where you have made edits in the file. (Ctrl+minus)
gen.regpy('Ctrl+-','G Navigate Back', 'plugins.plugin_recordposition.goBack()')
gen.regpy('Ctrl+Shift+-','G Navigate Forward', 'plugins.plugin_recordposition.goForward()')

# copy current filepath (Ctrl+1)
gen.reg(None,'G Copy filepath', r'"$(pyplugin.lnzpath)" "$(SciteDefaultHome)\plugins\plugin_shared\setclippath.jsz" "$(FileDir)"', subsys=Subsys.exec_async, n=1)

# switch between cpp and h
gen.regpy('Ctrl+Alt+H','Cpp Switch Header', 'plugins.plugin_switchheader.switchheader()', sFiletype='$(file.patterns.cpp)')


# personal plugins
if os.path.exists('nocpy_custom'):
    import nocpy_custom
    nocpy_custom.addcustom(gen)


print 'What was written:'
gen.write()
