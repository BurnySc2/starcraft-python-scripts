import sys
sys.path.append("..")

from sceneswitcher import *


# pytests
def test_scene_switch_mode_asap():
    sceneSwitcher = SceneSwitcher()
    sceneSwitcher.settings = {
        "loading_screen_mode": "asap",
    }
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.ui_response = {"activeScreens": ["Some random menu scene here"]} # Menu screen

    # Change scene from unknown to menu
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.MENU

    # From menu to game via loading screen only
    sceneSwitcher.ui_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From menu to game via game scene
    sceneSwitcher.ui_response = {"activeScreens": []} # In game screen
    sceneSwitcher.sc2_location = Location.MENU
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From game to replay
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using in game ui
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using loading screen ui, this might not work
    sceneSwitcher.i_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From replay to in game (resume from replay)
    sceneSwitcher.ui_response = {"activeScreens": []} # Game screen
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.sc2_location = Location.INREPLAY
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to ingame (in case of script restart midgame)
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to replay (in case of script restart midgame)
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY



def test_scene_switch_mode_fast():
    sceneSwitcher = SceneSwitcher()
    sceneSwitcher.settings = {
        "loading_screen_mode": "fast",
    }
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.game_response = {"isReplay": False, "displayTime": 0} # In game
    sceneSwitcher.ui_response = {"activeScreens": ["Some random menu scene here"]} # Menu screen

    # Change scene from unknown to menu
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.MENU

    # From menu to game via loading screen only
    sceneSwitcher.ui_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.game_response = {"isReplay": True, "displayTime": 100} # Was previously in replay, but now loading to new game
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.MENU

    # From menu to game via loading screen but game response is refreshed
    sceneSwitcher.ui_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # In game screen
    sceneSwitcher.game_response = {"isReplay": False, "displayTime": 0} # Game response updated
    sceneSwitcher.sc2_location = Location.MENU
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From menu to game via game scene
    sceneSwitcher.ui_response = {"activeScreens": []} # In game screen
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.sc2_location = Location.MENU
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From game to replay
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using in game ui
    sceneSwitcher.sc2_location = Location.MENU
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using loading screen ui, this might not work
    sceneSwitcher.i_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.game_response = {"isReplay": False} # Was previously in a game, this will only be updated during the loading process or when loading screen finished
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From menu to replay using loading screen ui, this might not work
    sceneSwitcher.i_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.game_response = {"isReplay": True} # This info now updated, so it should load the replay scene
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # Loading from game to menu should still show the game scene until the menu is loaded
    sceneSwitcher.sc2_location == Location.INGAME
    sceneSwitcher.i_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From replay to in game (resume from replay)
    sceneSwitcher.ui_response = {"activeScreens": []} # Game screen
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.sc2_location = Location.INREPLAY
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to ingame (in case of script restart midgame)
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to replay (in case of script restart midgame)
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY



def test_scene_switch_mode_delayed():
    sceneSwitcher = SceneSwitcher()
    sceneSwitcher.settings = {
        "loading_screen_mode": "delayed",
    }
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.ui_response = {"activeScreens": ["Some random menu scene here"]} # Menu screen

    # Change scene from unknown to menu
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.MENU

    # From menu to game via loading screen only
    sceneSwitcher.ui_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.MENU

    # From menu to game via game scene
    sceneSwitcher.ui_response = {"activeScreens": []} # In game screen
    sceneSwitcher.sc2_location = Location.MENU
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From game to replay
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using in game ui
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From menu to replay using loading screen ui, this might not work
    sceneSwitcher.i_response = {"activeScreens": ["ScreenLoading/ScreenLoading"]} # Loading screen
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY

    # From replay to in game (resume from replay)
    sceneSwitcher.ui_response = {"activeScreens": []} # Game screen
    sceneSwitcher.game_response = {"isReplay": False} # In game
    sceneSwitcher.sc2_location = Location.INREPLAY
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to ingame (in case of script restart midgame)
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INGAME

    # From unknown to replay (in case of script restart midgame)
    sceneSwitcher.game_response = {"isReplay": True} # In replay
    sceneSwitcher.sc2_location = Location.UNKNOWN
    sceneSwitcher.set_sc2_location(
        sceneSwitcher.convert_sc2_location_to_enum(
            sceneSwitcher.get_sc2_location(sceneSwitcher.ui_response, sceneSwitcher.game_response)))
    assert sceneSwitcher.sc2_location == Location.INREPLAY