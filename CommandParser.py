
class commandLineInterface:
    def __init__(self):
        self.mods = None
        self.sysExit = False
        self._Commands = {}
    def setTop(self,top):
        self.top = top
        self._Commands = {
            "setsession": (self.top.recorder.setSessionName,1),
            "ss": (self.top.recorder.setSessionName,1),

            "startRecording": (self.top.recorder.startRecording,0),
            "R": (self.top.recorder.startRecording,0),

            "stopRecording": (self.top.recorder.stopRecording,0),
            "X": (self.top.recorder.stopRecording,0),

            "exit": (self.exit,0),
            "help": (self.printHelp,0)
        }
    def exit(self):
        self.top.exit()
        self.sysExit =True

    def printHelp(self):
        for item in self._Commands.keys():
            print(item)

    def parseAndExecute(self,commandstring):
        tokens = commandstring.split(" ")
        if len(tokens) < 1:
            print("Invalid Command")
            return None
        cmdFunc = self._Commands.get(tokens[0])
        if cmdFunc == None:
            print("Invalid Command")
            return None
        if len(tokens[1:]) != cmdFunc[1]:
            print("Wrong Number of Args. Correct num args: " + str(cmdFunc[1]) )
        cmdFunc[0](*tokens[1:])
        
    def run(self):
        while not self.sysExit:
            self.parseAndExecute(input("input Command: "))
        