

// This function is executed on script start and contains an object with all the settings data (e.g. pre-filled GUI data from last script usage)
eel.expose(init_gui_data);
function init_gui_data(settings_json) {
    console.log(settings_json)
    document.getElementById('enabled').checked = settings_json["enabled"]
    document.getElementById('end_when_sc2_closes').checked = settings_json["end_when_sc2_closes"]
    document.getElementById('end_when_obs_closes').checked = settings_json["end_when_obs_closes"]
    document.getElementById('caster_mode').checked = settings_json["caster_mode"]
    document.getElementById('loading_screen_mode').value = settings_json["loading_screen_mode"]
    document.getElementById('menu_scene').options.add(new Option(settings_json["menu_scene"], settings_json["menu_scene"], true));
    document.getElementById('game_scene').options.add(new Option(settings_json["game_scene"], settings_json["game_scene"], true));
    document.getElementById('replay_scene').options.add(new Option(settings_json["replay_scene"], settings_json["replay_scene"], true));
    document.getElementById('caster_menu_scene').options.add(new Option(settings_json["caster_menu_scene"], settings_json["caster_menu_scene"], true));
    document.getElementById('caster_game_scene').options.add(new Option(settings_json["caster_game_scene"], settings_json["caster_game_scene"], true));
    document.getElementById('caster_replay_scene').options.add(new Option(settings_json["caster_replay_scene"], settings_json["caster_replay_scene"], true));
}

// This function is triggered on click of the button on the GUI to ask Python for all the active OBS Studio scenes
function py_get_scene_names() {
    eel.get_obs_scene_names()(scene_names => get_scene_names(scene_names))
}

// Callback function of the above
function get_scene_names(scene_names) {
    console.log("Updating scenes from OBS Studio");
    console.log(scene_names); // This should contain OBS Studio scene names, e.g.: ["myGameScene", "myMenuScene", "myReplayScene"]
    // If array is empty: No connection to OBS could be made or no scenes are set up
    var scene_element_names = ["menu_scene", "game_scene", "replay_scene", "caster_menu_scene", "caster_game_scene", "caster_replay_scene"];
    for (let i = 0; i < scene_element_names.length; i++) {
        var element = document.getElementById(scene_element_names[i]);
        var chosen_name = element.value;
        clear_select_options(element);
        add_options(element, scene_names, chosen_name);
    }
}

// Clear all select options
function clear_select_options(element) {
    for (var i = element.options.length - 1; i >= 0; i--) {
        element.remove(i);
    }
}

// Add select options to dropdown menu to choose from
function add_options(element, options_array, chosen_name) {
    element.options.add(new Option(chosen_name, chosen_name, true));
    for (var i = 0, l = options_array.length; i < l; i++) {
        var option = options_array[i];
        if (option == chosen_name) {
//            console.log("Found selected element: " + chosen_name)
//            element.options.add(new Option(option, option, true));
        } else {
            element.options.add(new Option(option, option, false));
        }
    }
}

eel.expose(py_exit_script);
function py_exit_script() {
    eel.exit_script();
    window.close()
}

// This function is called when any GUI Input element changes, e.g. the user changes the assigned scene for "in Menu"
function send_scenes_mapping_to_python() {
    var current_settings = {
        "enabled": document.getElementById('enabled').checked,
        "end_when_sc2_closes": document.getElementById('end_when_sc2_closes').checked,
        "end_when_obs_closes": document.getElementById('end_when_obs_closes').checked,
        "caster_mode": document.getElementById('caster_mode').checked,
        "loading_screen_mode": document.getElementById('loading_screen_mode').value,
        "menu_scene": document.getElementById('menu_scene').value,
        "game_scene": document.getElementById('game_scene').value,
        "replay_scene": document.getElementById('replay_scene').value,
        "caster_menu_scene": document.getElementById('caster_menu_scene').value,
        "caster_game_scene": document.getElementById('caster_game_scene').value,
        "caster_replay_scene": document.getElementById('caster_replay_scene').value,
    };
    console.log(current_settings);
    eel.update_sc2_location_to_scenes_mapping(current_settings);
}

