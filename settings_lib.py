import os, json
import Command


class Settings:
    def __init__(self, commands: list[Command.Command], settingsPath):
        self.commands = commands
        self.settings = Settings.loadSettings(settingsPath)

    @staticmethod
    def loadSettings(commands, settingPath):
        if not os.path.exists(settingPath):
            Settings.createDefaultSettings(commands, settingPath)
        return json.load(open(settingPath, "r"))

    @staticmethod
    def createDefaultSettings(commands, settingsPath):
        settings = {}
        for command in commands:
            commandObject = commands[command]
            commandName = commandObject.getName()
            commandOptions = commands[command].getOptions()
            settings[commandName] = {}
            for option in commandOptions:
                optionObject = commandOptions[option]
                optionName = optionObject.getName()
                settings[commandName][optionName + "DefaultValue"] = optionObject.defaultValue
        open(settingsPath, "w").write(json.dumps(settings, indent=4))