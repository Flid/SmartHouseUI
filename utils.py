from auto_updater import AutoUpdater, get_git_root

def self_update():
    AutoUpdater(
        'master',
        get_git_root(__file__),
    ).run()