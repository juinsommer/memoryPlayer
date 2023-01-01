import os
import subprocess

class GenerateScript:
    def __init__(self):
        self.command_script_name = "commands-to-rpi.sh"
        self.getter_script_name = "get-fileNames.sh"
        self.upload_script_name = "upload-file.sh"
        self.omni_file_name = "omni-epd.ini"
        self.options_file_name = "slowmovie.conf"
        self.options_file = open(self.options_file_name, "w")
        self.options = ["random-frames = false\n", 
                              "epd = waveshare_epd.epd7in5_V2\n", 
                              "contrast = 1.0\n",
                              "clear = true\n"
                              "fullscreen = true\n"]
        self.pwd = subprocess.run(["pwd"], capture_output=True, text=True).stdout.rstrip()
        self.command_file = open(self.command_script_name, "w")
        self.current_options = []
        self.initOptions()
        self.lines = ["#!/usr/bin/env bash\n", ". remote-settings.sh\n"]
        self.initGetterScript()
        self.play_select = None
        self.frames_per_interval = None
        self.delay = None
        self.rotateValue = None
        self.currentOmniFile()
        self.stop_service = "'sudo systemctl stop slowmovie;'"
        self.start_service = "'sudo systemctl start slowmovie;'"
        self.check_service_status = "'systemctl status slowmovie;'"
        
    def initOptions(self):
        # Copy config file with current options and store in current_options
        os.system(". " + self.pwd + "/remote-settings.sh\nscp -q $HOST:$RUN_PATH/" 
                    + self.options_file_name + " " + self.pwd + "/slowmovie_copy.conf")

        with open("slowmovie_copy.conf", "r") as f:
            contents = f.read()

        f.close()
        os.system("rm -f slowmovie_copy.conf")
        self.current_options = contents.split("\n")
    
    def initGetterScript(self):
        getterFile = open(self.getter_script_name, "w")
        getterFile.write(self.lines[0] + self.lines[1])
        getterFile.write("ssh $HOST ls $VID_PATH")
        getterFile.close()
        os.system("chmod +x " + self.getter_script_name + "\nwait")

    def uploadFile(self, path_to_file):
        uploadFile = open(self.upload_script_name, "w")
        uploadFile.write(self.lines[0] + self.lines[1])
        uploadFile.write("scp " + path_to_file + " $HOST:$VID_PATH") 
        uploadFile.close()

        os.system("chmod +x " + self.upload_script_name + "\nwait")
        status = subprocess.run(["./" + self.upload_script_name], capture_output=True, text=True)
        os.system("rm -f " + self.upload_script_name)

        if status.returncode == 0:
            return True
        else:
            return False
    
    def currentOmniFile(self):
        os.system(". " + self.pwd + "/remote-settings.sh\nscp -q $HOST:$RUN_PATH/"
                       + self.omni_file_name + " " + self.pwd + "/omni-epd-copy.ini")

        with open("omni-epd-copy.ini", "r") as f:
            contents = f.read()

        f.close()

        os.system("rm -f omni-epd-copy.init")
        self.current_omni = contents.split("\n")
        self.current_omni.pop(0) # Remove "[Display]"
        self.rotateValue = self.current_omni[0]
        print(self.rotateValue)

    def cancel(self):
        os.system("rm -f " + self.command_script_name 
                + "\nrm -f " + self.getter_script_name
                + "\nrm -f " + self.options_file_name
                + "\nrm -f " + "omni-epd-copy.init"
                + "\nrm -f " + self.omni_file_name)
    
    def playSelected(self, path_to_file):
        if self.play_select != None:
            [self.options.pop(self.options.index(line)) for line in self.options if "file" in line]

        self.play_select = "Videos/" + path_to_file
        self.options.append("file = " + self.play_select + "\n")
            
    def setOptions(self):
        # No changes made, so close file
        if len(self.options) == 4:
            self.options_file.close()

        else:
            if self.play_select == None:
                [self.options.append(self.current_options[self.current_options.index(line)] + "\n") 
                for line in self.current_options if "file" in line]

            if self.delay == None:
                [self.options.append(self.current_options[self.current_options.index(line)] + "\n") 
                for line in self.current_options if "delay" in line]
            
            if self.frames_per_interval == None:
                [self.options.append(self.current_options[self.current_options.index(line)] + "\n") 
                for line in self.current_options if "increment" in line]

            [self.options_file.write(option) for option in self.options]
            self.options_file.close()
            # Copy new option changes to device
            os.system(". " + self.pwd + "/remote-settings.sh" +"\nscp -q " 
                        + self.options_file_name +" $HOST:$RUN_PATH")

        os.system("rm -f " + self.options_file_name)

    def getFileNames(self):
        directory = subprocess.run(["./" + self.getter_script_name], capture_output=True, text=True)
        if directory.returncode == 0:
            listDirectory = directory.stdout.splitlines() # each file string separated by new line
            return listDirectory

        else:
            raise Exception("\nAccess to device directory failed: stderr=" + directory.stderr + "\n")

    def deleteFile(self, path_to_file):
        os.system(". " + self.pwd + "/remote-settings.sh\n" 
                    + "ssh $HOST rm $VID_PATH/" + path_to_file)

    def setInterval(self, interval):
        if self.delay != None:
            [self.options.pop(self.options.index(line)) for line in self.options if "delay" in line]

        self.delay=str(interval)
        self.options.append("delay = " + self.delay + "\n")

    def setFramesPerInterval(self, fpi):
        if self.frames_per_interval != None:
            [self.options.pop(self.options.index(line)) for line in self.options if "increment" in line]

        self.frames_per_interval = str(fpi)
        self.options.append("increment = " + self.frames_per_interval + "\n")

    def rotateImage(self):
        if self.rotateValue == "rotate = 360":
            self.rotateValue = "rotate = 90"

        elif self.rotateValue == "rotate = 270":
            self.rotateValue = "rotate = 360"

        elif self.rotateValue == "rotate = 180":
            self.rotateValue = "rotate = 270"

        elif self.rotateValue == "rotate = 90":
            self.rotateValue = "rotate = 180"

        print(self.rotateValue)

        self.omniFile = open(self.omni_file_name, "w")
        self.omniFile.write("[Display]\n" + self.rotateValue + "\n")
        self.omniFile.close()
        
        # Restart service to view rotated image
        os.system(". " + self.pwd + "/remote-settings.sh\nscp -q "
                    + self.omni_file_name + " $HOST:$RUN_PATH" + "\nssh $HOST "
                    + self.stop_service + self.start_service)

        os.system("rm -f " + self.omni_file_name)

    def shutdownDevice(self):
        os.system(". "  + self.pwd + "/remote-settings.sh\n" + "ssh $HOST sudo shutdown now")

    def execFile(self):
        self.setOptions()

        # Restart service if options have changed
        if len(self.options) > 5:
            self.lines.append("ssh $HOST " + self.stop_service)
            self.lines.append(" " + self.start_service)
            [self.command_file.write(line) for line in self.lines]
            self.command_file.close()

            os.system("chmod +x " + self.command_script_name) # make file executable
            process = subprocess.run(["./" + self.command_script_name], capture_output=True)

            if process.returncode != 0:
                raise Exception(self.command_script_name + " failed. stderr=" + process.stderr.decode() + "\n")
            
        else:
            self.command_file.close()

        self.cancel()

if __name__ == "__main__":
    gs = GenerateScript()
    gs.rotateImage()
