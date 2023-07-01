from v2enlib import utils, const

def test_playNotes():
    assert utils.playNotes(*const.sound_tracks['macos_startup'])