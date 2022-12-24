import os
import subprocess

class GenerateScript:
    def __init__(self):
        self.script = "commands-to-rpi.sh"
        self.getter_script = "get-fileNames.sh"
        self.file = open(self.script, "w")
        self.getterFile = open(self.getter_script, "w")
        self.lines = ["#!/usr/bin/env bash\n", ". remote-settings.sh\n"]
        self.uploadFiles = []

    def uploadFile(self, path_to_file):
        self.uploadFiles.append(path_to_file)
        self.lines.append("scp " + path_to_file + " $HOST:$RPI_PATH")
    
    def cancel(self):
        os.system("rm -f " + self.script + "\nrm -f " + self.getter_script)
    
    def playSelected(self, path_to_file):
        pass

    def getFileNames(self):
        self.getterFile.write(self.lines[0] + self.lines[1])
        self.getterFile.write("ssh $HOST ls $RPI_PATH")
        self.getterFile.close()

        os.system("chmod +x " + self.getter_script + "\nwait")
        directory = subprocess.run(["./" + self.getter_script], capture_output=True, text=True)
        listDirectory = directory.stdout.splitlines()

        return listDirectory

    # def deleteFile(self):

    def execFile(self):
        if len(self.lines) > 2:
            [self.file.write(line) for line in self.lines]
            self.file.close()
            os.system("chmod +x " + self.script) # make file executable
            os.system("./" + self.script + "\nwait\nexit") # execute script, wait until done, close session

        self.cancel()

if __name__ == "__main__":
    gs = GenerateScript()
    gs.getFileNames()