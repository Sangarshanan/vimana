import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]

cx_Freeze.setup(
    name="Vimana: A Space Shooter",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["fonts/", "images/"]}},
    executables = executables

    )
