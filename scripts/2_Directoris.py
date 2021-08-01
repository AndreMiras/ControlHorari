import os

dir_path = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(dir_path + "/../codis"):
    os.makedirs(dir_path + "/../codis")

if not os.path.exists(dir_path + "/../informes"):
    os.makedirs(dir_path + "/../informes")

if not os.path.exists(dir_path + "/../files"):
    os.makedirs(dir_path + "/../files")

if not os.path.exists(dir_path + "/../logs"):
    os.makedirs(dir_path + "/../logs")