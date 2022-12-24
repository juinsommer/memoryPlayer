import os
import subprocess

class GenerateScript:
    def __init__(self):
        self.script = "commands-to-rpi.sh"
        self.getter_script = "get-fileNames.sh"
        self.upload_script = "upload-file.sh"
        self.cancel()
        self.file = open(self.script, "w")
        self.options = []
        self.lines = ["#!/usr/bin/env bash\n", ". remote-settings.sh\n"]
        self.initGetterScript()
        self.playSelect = None

    def initGetterScript(self):
        getterFile = open(self.getter_script, "w")
        getterFile.write(self.lines[0] + self.lines[1])
        getterFile.write("ssh $HOST ls $VID_PATH")
        getterFile.close()
        os.system("chmod +x " + self.getter_script + "\nwait")

    def uploadFile(self, path_to_file):
        uploadFile = open(self.upload_script, "w")
        uploadFile.write(self.lines[0] + self.lines[1])
        uploadFile.write("scp " + path_to_file + " $HOST:$VID_PATH") 
        uploadFile.close()

        os.system("chmod +x " + self.upload_script + "\nwait")
        status = subprocess.run(["./" + self.upload_script], capture_output=True)
        os.system("rm -f " + self.upload_script)

        if status.returncode == 0:
            print("\nUpload of " + path_to_file + " successful.\n")

        else:
            raise Exception("\nUpload of " + path_to_file + " failed. stderr=" + status.stderr + "\n")
        
    
    def cancel(self):
        os.system("rm -f " + self.script + "\nrm -f " + self.getter_script)
    
    def playSelected(self, path_to_file):
        self.playSelect = path_to_file
        self.options.insert(0, " -f $VID_PATH/" + self.playSelect)
            
    def setOptions(self):
        options = "".join(self.options)
        self.lines.append("ssh $HOST .$RUN_PATH/slowmovie.py" + options + "\n")

    def getFileNames(self):
        directory = subprocess.run(["./" + self.getter_script], capture_output=True, text=True)
        if directory.returncode == 0:
            listDirectory = directory.stdout.splitlines() # each file string separated by new line
            return listDirectory

        else:
            raise Exception("\nAccess to device directory failed: stderr=" + directory.stderr + "\n")

    def deleteFile(self, path_to_file):
        self.lines.append("ssh $HOST rm $VID_PATH/" + path_to_file + "\n")

    def setInterval(self, interval):
        self.options.append(" -d " + interval)

    def setFramesPerInterval(self, fpi):
        self.options.append(" -i " + fpi)

    def showOptions(self):
        return "".join(self.options) if self.options else ""

    #TODO: Add error checking and display to UI
    def execFile(self):
        if len(self.lines) > 2:
            if len(self.options) > 0:
                print(self.showOptions())
                self.setOptions()

            [self.file.write(line) for line in self.lines]
            self.file.close()
            os.system("chmod +x " + self.script) # make file executable
            process = subprocess.run(["./" + self.script], capture_output=True)

            if process.returncode != 0:
                raise Exception(self.script + " failed. stderr=" + process.stderr.decode() + "\n")

        #self.cancel()

if __name__ == "__main__":
    gs = GenerateScript()
    gs.getFileNames()