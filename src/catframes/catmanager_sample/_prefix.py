#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import threading
import platform
import random
import time
import signal
import sys
import os
import io
import re
import copy
import shutil
import base64
import configparser

# import requests

import tempfile
import logging
from logging.handlers import WatchedFileHandler
from pathlib import Path

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser, scrolledtext
from unittest import TestCase
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
try:
    from PIL import Image, ImageTk
    PIL_FOUND_FLAG = True
except:
    PIL_FOUND_FLAG = False


#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.


# коэффициент масштабирования окна в линуксе
LINUX_SIZING = 1.1

USER_DIRECTORY = os.path.expanduser("~")
CONFIG_FILENAME = ".catmanager.ini"
PREVIEW_DIRNAME = ".cat_temp"
PREVIEW_FILENAME = ".preview.{ex}"

DEFAULT_CANVAS_COLOR = "#000000"  # цвет стандартного фона изображения

# Цвета для главного окна
MAIN_TOOLBAR_COLOR = "#E0E0E0"
MAIN_TASKLIST_COLOR = "#CDCDCD"
MAIN_TASKBAR_COLORS = {"Running": "#E0E0E0", "Error": "#FF9B9B", "Success": "#6AFB84"}

# константы имён ошибок
INTERNAL_ERROR = "internal"
NO_FFMPEG_ERROR = "noffmpeg"
NO_CATFRAMES_ERROR = "nocatframes"
START_FAILED_ERROR = "failed"

SYSTEM_PATH = "system_path"

FOLDER_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA
6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAA7AAAAOwAFq1okJAAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJTUUH6AcU
DwU7nLh1ywAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNC0wNy0yMFQxNTowNTo1OCswMDowMNM5N1wAAAAldEVYdGRhdGU6bW9k
aWZ5ADIwMjQtMDctMjBUMTU6MDU6NTgrMDA6MDCiZI/gAAAAVElEQVQ4T2OgFmAEEf8XMPwH87AAxgSIGkKAEZ8hMECMYRCD
tDSgXPIAo9kNRsb/pzQIuogYwASlKQajBhEGowYRBoPPIEgxQmF+A2VaKJNSwMAAALsJEQz8R0D5AAAAAElFTkSuQmCC
"""

PALETTE_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
DsEAAA7BAbiRa+0AAAJKSURBVDhPdZTLb01RFIfXKerZ1vtZ79DUSGIgJg0zj8Sgf4GhoaGRhH+AxNiQiH+gREJEECFhIhIi
IW5FEJVe1dbF8X377t3eeqzk22vvc/b97bXWWftWNRb/sqEq4h1eJhcz9Lepb+H/tq7sZ+00AidgEfNuSDtYpwWC1Uk458M5
NlfoEj9Yju+FpTAj5LAQloEv2VRdi2i2mLdtVmgEkR68exUxG4UMJm1zsQSKGPQ+wretLfSS3WvwazPOV4KC8yHmgQI+XAfr
s4fqM74I+XxjJtc0NsAqWABpcOGLLR30x2QSR2iU2MdIqaXINtgJuzPuNZs0bIdB2AMDMYZwg7q9YfWEhKr7ddRmbynF7M2s
q8HwAM7r9zOcgYPxHtGPzJownfkO1RWErKc5itUoZTXIgesMR0biXhxOLfUN/FY/4VfGRqwuIOSkPPwBnjABo3DZVIaexdG7
beHSFX6DcriBVKcQ8odTYJjjYOivkt/HeDHixoGIs6ROqjt4Yup2iqWwb/0U1TBChvsVjEKRRjpnLxwDOvkpsVxlehueR/RR
oNVMS1fp010bJLgvLCzgRCr3LlDoEByPeMH5XrGHgFC8hg+IUJM+pg28RxNB8DW6EbHJFBE/tw1GAp1ttDWzmSy4KdZRS0LN
VPfSieyITaCo51HWzsa289XPlP+OJKTVqbwroNxaf0k0NVvcZWVLUfJVG3+MzzYjpNVxk9EyerS7ubn2RBFSxCA5r2Zrj72Q
7b9/bFXcYaROLe7JJ6ZvgWLWw7790yJ+A6mSiwF9eeKxAAAAAElFTkSuQmCC
"""

PLAY_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
DsMAAA7DAcdvqGQAAABeSURBVDhPzdCxDcAgDERRZmEelmVCJ1eArJMJtinCk67B0i8o8qq9zWnW24orxO8Wd4hvLBTiuxYO
YZZUCGPpEKYdhbDhOITBPaHh/89mqZAlHFoJhb64Qzuu0J7IA1aJ3KICtYk1AAAAAElFTkSuQmCC
"""

ERROR_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
Dr0AAA69AUf7kK0AAADPSURBVEhLtZTBDcIwDEUNI/TMkRnYgzM7MAw7cIU56C6wQhpbSVUSfzug5EtRo8R+cr/d7t6HY6AB
2qdnd31VPN3uaUf0uV7SzhbKWcEScD7Joeg5u3ArB1sRE7bVlKqghWyPAdyDitiKvMLjFVTF819ieFXjBquJ/onAXdkPdY6b
XjULNFn1WAJzhZYAlAWb58INKGvYlwfBrs/xThvFLBXc3DwDXoEhlP3WPEfw7VD3/EBWcGtCa6w9FWCkWuYcg5059eDjf/S9
ZXv8t4gWlzE1GW5peVYAAAAASUVORK5CYII=
"""

OK_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
Dr0AAA69AUf7kK0AAAC5SURBVEhL1ZXbCYRADEXjVuC/f7ZgGws2sWVtExZiGf5vBy4XJpJ5JGYdhfXA4CB6c8gEbfrpudIF
PML1dKqN5+EVdkTD/A67SmOEtt24LVnkslYcDmZbjf8yLtl+lum8w7OIxk0bHYnHFmzG/AIvWYQp3dNQW6GFe2yB2WMZ/ost
yHqcGgFYAa8tiIzxEIdIEFgqaJG1QgtPsWxBscfecAv18KzwPVtgTkWNuetDn47ani242z+P6Atnwl4nWv9uvAAAAABJRU5E
rkJggg==
"""
