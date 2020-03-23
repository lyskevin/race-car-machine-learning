
class commandLineInterface:

    def __init__(self,mods):
        self.mods = mods
        self.sysExit = False
        self._Commands = {
            "setsession": mods["recorder"].setSessionName,
            "ss": mods["recorder"].setSessionName,

            "startRecording": mods["recorder"].startRecording,
            "R": mods["recorder"].startRecording,

            "stopRecording": mods["recorder"].stopRecording,
            "X": mods["recorder"].stopRecording,

            "exit": self.exit,
            "help": self.printHelp
        }
    def exit(self):
        for n,mod in self.mods.items():
            if not n == "actuator":
                mod.exit()
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
        cmdFunc(*tokens[1:])
        
    def run(self):
        while not self.sysExit:
            self.parseAndExecute(input("input Command: "))
        