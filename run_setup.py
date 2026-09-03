import sys

if len(sys.argv) > 1:
    import folderguard.launcher
    folderguard.launcher.main()
else:
    import folderguard.setup_gui