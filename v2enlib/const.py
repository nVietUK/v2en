import yaml, tensorflow_model_optimization as tfmot
from v2enlib import utils
from translators import server as TransServer

try:
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    target = cfg["v2en"]["target"]
    first_lang = target[:2]
    second_lang = target[-2:]
    accept_percentage = cfg["v2en"]["accept_percentage"]
    time_allow = cfg["v2en"]["allow"]["time"]
    resource_allow = cfg["v2en"]["allow"]["resource"]
    thread_alow = cfg["v2en"]["thread"]["allow"]
    thread_limit = cfg["v2en"]["thread"]["limit"]
    table_name = cfg["sqlite"]["table_name"]
    trans_timeout = cfg["v2en"]["trans_timeout"]
    initial_sparsity = cfg["training"]["initial_sparsity"]
    final_sparsity = cfg["training"]["final_sparsity"]
    begin_step = cfg["training"]["begin_step"]
    end_step = cfg["training"]["end_step"]
    learning_rate = cfg["training"]["learning_rate"]
    allow_pruning = cfg["training"]["allow_pruning"]
    disableTQDM = not cfg['v2en']['allow']['tqdm']
    pruning_params = {
        "pruning_schedule": tfmot.sparsity.keras.PolynomialDecay(
            initial_sparsity=initial_sparsity,
            final_sparsity=final_sparsity,
            begin_step=begin_step,
            end_step=end_step,
        ),
    }
    trans_dict = TransServer.TranslatorsServer().translators_dict
    sound_tracks = {
        "macos_startup": [
            ["F#2", "C#3", "F#3", "C#4", "F#4", "A#4"],
            [5 / 3] * 6,
            [0] * 6,
        ],
        "windows7_shutdown": [
            ["G#4", "E4", "B4", "C5"],
            [0.25, 0.25, 0.25, 0.25],
            [0.0, 0.3, 0.6, 0.9],
        ],
    }
except Exception as e:
    utils.printError("importing config", e, True)
    exit()
