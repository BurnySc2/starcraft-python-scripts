# Testing
from dpcontracts import require, ensure
from hypothesis import given
from hypothesis.strategies import text, integers, floats

# Communication with OBS Studio
from obswebsocket import obsws, requests as obsrequest
from obswebsocket.exceptions import ConnectionFailure

# Communication with Browser GUI
import eel

# Commuinication with SC2 API
import requests

from enum import Enum
import json, os, threading
import time

import sys
print(sys.version)

class Location(Enum):
    UNKNOWN = 0
    MENU = 1
    LOADINGSCREEN = 2
    INGAME = 4
    INREPLAY = 5
    SC2NOTRUNNING = 6


@eel.expose
def update_sc2_location_to_scenes_mapping(scenes_json):
    global sceneSwitcher
    sceneSwitcher.settings.update(scenes_json)

@eel.expose
def get_obs_scene_names(): # type: () -> List[str]
    global sceneSwitcher
    scene_names = sceneSwitcher.get_obs_scenes()
    # print(scene_names)
    return scene_names

@eel.expose
def exit_script():
    global sceneSwitcher
    sceneSwitcher.stop_script = True

class SceneSwitcher:
    def __init__(self):
        self.sc2_location = Location.UNKNOWN
        self.settings_path = "settings.json"
        self.threading_lock = threading.Lock()
        self.settings = None # type: dict
        self.ws = None # type: obsws
        self.connected = False
        self.stop_script = False
        self.last_set_scene = ""

        # Required to auto-shutdown script when sc2 or obs was closed
        self.thread_locked_for_x_seconds = 0
        self.starcraft_is_running = False
        self.established_connection_obs_once = False
        self.starcraft_detected_once = False

    def __enter__(self):
        self.load_settings()
        # Send settings data to GUI
        eel.init_gui_data(self.settings)
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        self.save_settings()

    def connect(self):
        try:
            self.ws = obsws(self.settings["host"], self.settings["port"], self.settings["password"])
            self.ws.connect()
            self.connected = True
            self.established_connection_obs_once = True
        except ConnectionFailure:
            pass

    def disconnect(self):
        if self.connected and self.ws is not None:
            self.ws.disconnect()
        self.connected = False

    def load_settings(self):
        """ Loads settings from local settings.json file """
        # Set the default settings. In case in a later version of this script the settings change, new default variables will be added automatically
        self.settings = {
                # Connection settings to OBS Studio websockets plugin
                "host": "localhost",
                "port": 4444,
                "password": "",
                "update_frequency": 1, # seconds, how often the script loads the SC2 UI location
            }
        if os.path.isfile(self.settings_path):
            with open(self.settings_path) as f:
                self.settings.update(json.load(f))

    def save_settings(self):
        """ Saves settings to local settings.json file """
        with open(self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    @ensure("Function needs to return a list of strings", lambda args, result: all(isinstance(x, str) for x in result))
    def get_obs_scenes(self): # type: () -> List[str]
        """ Retrieves all created scene names from OBS Studio """
        if not self.connected:
            self.connect()
        if self.connected:
            scenes = self.ws.call(obsrequest.GetSceneList())
            scene_names = [scene["name"] for scene in scenes.datain["scenes"]] # type: List[str]
            return scene_names
        return []

    def update_scenes_thread(self):
        """ Execute the function below as a seperate thread """
        if not self.settings.get("enabled", False):
            return
        if not self.connected:
            self.connect()
        threading.Thread(target=self.update_scenes, args=()).start()

    def update_scenes(self):
        """ Executes the whole process of getting current sc2 scene, and setting the scene if it changed. """
        if self.connected and not self.threading_lock.locked():
            self.thread_locked_for_x_seconds = 0
            with self.threading_lock:
                try:
                    # self.ui_response = requests.get("http://localhost:6119/ui").json()
                    # self.game_response = requests.get("http://localhost:6119/game").json()
                    self.ui_response = requests.get("http://localhost:6119/ui", timeout=(0.001, 0.1)).json()
                    self.game_response = requests.get("http://localhost:6119/game", timeout=(0.001, 0.1)).json()
                    self.starcraft_detected_once = True
                    self.starcraft_is_running = True
                    current_location = self.get_sc2_location(self.ui_response, self.game_response)
                    current_location_enum = self.convert_sc2_location_to_enum(current_location)
                    if current_location_enum != self.sc2_location:
                        self.set_sc2_location(current_location_enum)
                        self.switch_obs_scene()
                except requests.exceptions.ConnectionError:
                    # Sc2 not running, or wrong ip or port set
                    self.starcraft_is_running = False
                    return "sc2 not running"
                except requests.exceptions.ReadTimeout:
                    # When sc2 is in any loading screen, this might happen and sc2 becomes inresponsive
                    return "sc2 took too long to respond"
                except json.decoder.JSONDecodeError:
                    # This might occur on starcraft launch
                    return "could not decode json object"
        else:
            self.thread_locked_for_x_seconds += 1
            # print("Not connected or thread is locked")
            pass

    @require("UI response needs to be a dict", lambda args: isinstance(args.ui_response, dict))
    @require("Game response needs to be a dict", lambda args: isinstance(args.game_response, dict))
    @ensure("Result needs to be a string", lambda args, result: isinstance(result, str))
    def get_sc2_location(self, ui_response, game_response): # type: (dict, dict) -> str
        """ Gets the current scene from SC2 API """
        if ui_response["activeScreens"] == []:
            if game_response["isReplay"]:
                return "replay"
            else:
                return "game"
        elif ui_response["activeScreens"] == ["ScreenLoading/ScreenLoading"]:
            return "loading"
        else:
            return "menu"

    @require("Input needs to be a string", lambda args: isinstance(args.sc2_location, str))
    @ensure("Output needs to be an enum of type Location", lambda args, result: isinstance(result, Location))
    def convert_sc2_location_to_enum(self, sc2_location): # type: (str) -> Location
        location_dict = {
            "game": Location.INGAME,
            "menu": Location.MENU,
            "replay": Location.INREPLAY,
            "loading": Location.LOADINGSCREEN,
            "sc2 not running": Location.SC2NOTRUNNING,
        }
        return location_dict.get(sc2_location, Location.UNKNOWN)

    @require("Input needs to be an enum of type Location", lambda args: isinstance(args.target_location, Location))
    def set_sc2_location(self, target_location): # type: (Location) -> None
        """ Sets scene in OBS Studio based on current settings """

        if target_location == Location.MENU:
            self.sc2_location = Location.MENU

        elif target_location == Location.INREPLAY:
            self.sc2_location = Location.INREPLAY

        elif target_location == Location.INGAME:
            self.sc2_location = Location.INGAME

        # Priotize switching from menu to in game asap (when loading screen is detected, might switch wrong, e.g. when loading from menu to replay)
        elif (self.settings["loading_screen_mode"] == "asap"
                and self.sc2_location in {Location.MENU, Location.UNKNOWN}
                and target_location == Location.LOADINGSCREEN):
            self.sc2_location = Location.INGAME

        # Priotize switching from menu to in game as soon as it is known that a new game was started
        elif (self.settings["loading_screen_mode"] == "fast"
                and self.sc2_location in {Location.MENU, Location.UNKNOWN}
                and target_location == Location.LOADINGSCREEN
                and not self.game_response["isReplay"]
                and self.game_response["displayTime"] == 0):
            self.sc2_location = Location.INGAME

    def get_target_scene_name(self) -> str:
        if not self.settings.get("caster_mode", False):
            # Use player scenes
            scenes_dict = {
                Location.INGAME: self.settings.get("game_scene", ""),
                Location.MENU: self.settings.get("menu_scene", ""),
                Location.INREPLAY: self.settings.get("replay_scene", ""),
            }
        else:
            # Use caster scenes
            scenes_dict = {
                Location.INGAME: self.settings.get("caster_game_scene", ""),
                Location.MENU: self.settings.get("caster_menu_scene", ""),
                Location.INREPLAY: self.settings.get("caster_replay_scene", ""),
            }
        # Return scene name if location is one of {INGAME, INMENU, INREPLAY}
        return scenes_dict.get(self.sc2_location, "")

    def switch_obs_scene(self):
        current_scene = self.last_set_scene
        target_scene = self.get_target_scene_name()
        # If scene name is assigned to a scene and is not the same scene name as current active scene
        if target_scene not in {"", current_scene}:
            # print(f"Changing scene to {target_scene}")
            self.last_set_scene = target_scene
            if self.connected:
                try:
                    self.ws.call(obsrequest.SetCurrentScene(target_scene))
                except ConnectionResetError:
                    # OBS was closed
                    self.connected = False

    def run(self):
        while 1:
            # self.update_scenes()
            self.update_scenes_thread()
            eel.sleep(self.settings["update_frequency"])
            # End the script when SC2 was detected at least once and SC2 is now closed
            if self.settings.get("end_when_obs_closes", False) and self.established_connection_obs_once and not self.connected:
                self.stop_script = True
            # End the script when OBS was detected at least once and OBS is now closed
            if self.settings.get("end_when_obs_closes", False) and self.starcraft_detected_once and not self.starcraft_is_running:
                self.stop_script = True
            # Close the window and end script
            if self.stop_script:
                eel.py_exit_script()
                break



def main():
    global sceneSwitcher
    try:
        eel.init("web")
        eel.start("index.html", size=(600, 400), block=False)
        with SceneSwitcher() as sceneSwitcher:
            sceneSwitcher.run()
    # Dump error message to file
    except Exception as e:
        print("Dumping error to file:", e)
        with open("error.txt", "w") as f:
            f.write(str(e))


if __name__ == "__main__":
    main()
