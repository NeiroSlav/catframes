#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time
import os
import re
from os.path import isfile, join
import random

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
from PIL import Image, ImageTk

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.



    #  из файла sets_utils.py:

"""
Класс языковых настроек содержит большой словарь, 
в котором для каждого языка есть соответсвия названия
виджета, и текста, который в этом виджете расположен.

Добавление нового ключа в этот словарь должно быть с
добавлением всех внутренних ключей по аналогии с другими.

Если в процессе будет допущена ошибка, или gui запросит
текст для виджета, который не прописан, в качестве текста
вернётся строка из прочерков "-----" для быстрого обнаружения. 
"""


class Lang:
    """Класс языковых настроек.
    Позволяет хранить текущий язык,
    И извлекать его текстовики.

    При добавлении новых языков в словарь data,
    их названия будут сами подтягиваться в поле настроек.
    """

    current_name = 'english'
    current_index = 0

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        'english': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Label 1',
            'root.openSets': 'Settings',
            'root.newTask': 'New task',

            'bar.active': 'processing',
            'bar.inactive': 'complete', 
            'bar.btInfo': 'Info',
            'bar.btCancel': 'Cancel',
            'bar.btDelete': 'Delete',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task',
            'task.lbColor': 'Background:',
            'task.lbFramerate': 'Framerate:',
            'task.lbQuality': 'Quality:',
            'task.cmbQuality': ('high', 'medium', 'poor'),
            'task.btCreate': 'Create',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',

            'warn.title': 'Warning',
            'warn.lbWarn': 'Warning!',
            'warn.lbText': 'Incomplete tasks!',
            'warn.btBack': 'Back',
            'warn.btExit': 'Leave',
        },
        'русский': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Строка 1',
            'root.openSets': 'Настройки',
            'root.newTask': 'Новая задача',

            'bar.lbActive': 'обработка',
            'bar.lbInactive': 'завершено', 
            'bar.btInfo': 'Инфо',
            'bar.btCancel': 'Отмена',
            'bar.btDelete': 'Удалить',

            'sets.title': 'Настройки',
            'sets.lbLang': 'Язык:',
            'sets.btApply': 'Применить',
            'sets.btSave': 'Сохранить',

            'task.title': 'Новая задача',
            'task.lbColor': 'Цвет фона:',
            'task.lbFramerate': 'Частота кадров:',
            'task.lbQuality': 'Качество:',
            'task.cmbQuality': ('высокое', 'среднее', 'низкое'),
            'task.btCreate': 'Создать',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            
            'warn.title': 'Внимание',
            'warn.lbWarn': 'Внимание!',
            'warn.lbText': 'Задачи не завершены!',
            'warn.btBack': 'Назад',
            'warn.btExit': 'Выйти',
        },
    }

    @staticmethod  # получение всех доступных языков
    def get_all() -> tuple:
        return tuple(Lang.data.keys())

    @staticmethod  # установка языка по имени или индексу
    def set(name: str = None, index: int = None) -> None:

        if name and name in Lang.data:
            Lang.current_index = Lang.get_all().index(name)
            Lang.current_name = name

        elif isinstance(index, int) and 0 <= index < len(Lang.data):
            Lang.current_name = Lang.get_all()[index]
            Lang.current_index = index

    @staticmethod  # получение текста по тегу
    def read(tag) -> Union[str, tuple]:
        try:
            return Lang.data[Lang.current_name][tag]
        except KeyError:  # если тег не найден
            return '-----'
            

class PortSets:
    """Класс настроек диапазона портов
    системы для связи с ffmpeg."""

    min_port: int = 10240
    max_port: int = 65535

    @classmethod
    def set_range(cls, min_port: int, max_port: int) -> None:
        if max_port - min_port < 100:
            raise AttributeError('range')
        if min_port < 10240:
            raise AttributeError('min')
        if max_port > 65535:
            raise AttributeError('max')

        cls.min_port = min_port
        cls.max_port = max_port

    @classmethod
    def get_range(cls) -> Tuple:
        return cls.min_port, cls.max_port
    




    #  из файла task_flows.py:

"""
Слой задач полностью отделён от gui.

Задачи создаются с помощью TaskManager, который
выдаёт им уникальные номера, и регистрирует их статусы.

При создании задачи, ей передаюётся нужная конфигурация,
которая представляет собой объект класса TaskConfig.
Атрибутами этого объекта являются все возможные параметры,
которые есть у консольной версии приложения catframes.
Этот объект имеет метод конвертирования в консольную команду,
которая и будет запущена самим процессом задачи при старте.

Чтобы в процессе обработки, задача могла как-то делиться
своим статусом с интерфейсом, реализован паттерн "наблюдатель".
При старте задачи, ей передаётся объект класса GuiCallback.
При инициализации, объект коллбэка принимает внешние зависимости,
чтобы у задачи была возможность обновлять свои статусы в gui.
"""



class TaskConfig:
    """Настройка и хранение конфигурации задачи.
    Создаётся и настраивается на слое gui.
    Позволяет конвертировать в команду catframes."""

    overlays_names = [
        '--top-left',
        '--top',
        '--top-right',
        '--right',
        '--bottom-right',
        '--bottom',
        '--bottom-left',
        '--left',
    ]

    quality_names = ('high', 'medium', 'poor')

    def __init__(self) -> None:
                
        self._dirs: List[str]                         # пути к директориям с изображениями
        self._overlays: Dict[str, str] = {}           # словарь надписей
        self._color: str = '#000'                     # цвет отступов и фона
        self._framerate: int                          # частота кадров
        self._quality: str                            # качество видео
        self._quality_index: int                      # номер значения качества
        self._limit: int                              # предел видео в секундах
        self._filepath: str                           # путь к итоговому файлу
        self._rewrite: bool = False                   # перезапись файла, если существует
        self._ports = PortSets.get_range()            # диапазон портов для связи с ffmpeg

    # установка директорий
    def set_dirs(self, dirs) -> list:
        self._dirs = dirs

    # установка оверлеев
    def set_overlays(self, overlays_texts: List[str]):
        self._overlays = dict(zip(self.overlays_names, overlays_texts))

    # установка цвета
    def set_color(self, color: str):
        self._color = color

    # установка частоты кадров, качества и лимита
    def set_specs(self, framerate: int, quality: int, limit: int = None):
        self._framerate = framerate
        self._quality_index = quality
        self._quality = self.quality_names[quality]
        self._limit = limit

    # установка пути файла
    def set_filepath(self, filepath: str):
        self._filepath = filepath

    def get_filepath(self) -> str:
        return self._filepath
    
    def get_dirs(self) -> list:
        return self._dirs[:]
    
    def get_quality(self) -> int:
        return self._quality_index
    
    def get_framerate(self) -> int:
        return self._framerate

    # создание консольной команды
    def convert_to_command(self) -> str:
        command = 'catframes'
    
        # добавление текстовых оверлеев
        for position, text in self._overlays.items():
            if text:
                command += f' {position}="{text}"'
        
        command += f" --margin-color {self._color}"         # параметр цвета
        command += f" --frame-rate {self._framerate}"       # частота кадров
        command += f" --quality {self._quality}"            # качество рендера

        if self._limit:                                     # ограничение времени, если есть
            command += f" --limit {self._limit}"

        if os.path.isfile(self._filepath):                  # флаг перезаписи, если файл уже есть
            command += f" --force"

        command += f" --port-range {self._ports[0]}:{self._ports[1]}"  # диапазон портов
        
        for dir in self._dirs:                              # добавление директорий с изображениями
            command += f' "{dir}"'
        
        command += f' "{self._filepath}"'                   # добавление полного пути файла    
        
        return command                                      # возврат собранной команды


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
            self,
            update_function,
            finish_function,
            delete_function,
            ):
        self.update = update_function
        self.finish = finish_function
        self.delete = delete_function
        
    
    @staticmethod  # метод из TaskBar
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(id: int):
        """сигнал о завершении задачи"""
        ...

    @staticmethod  # метод из RootWindow
    def delete(id: int):
        """сигнал об удалении задачи"""
        ...


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config = task_config
        self.command = task_config.convert_to_command()
        print(self.command)
        self.id = id  # получение уникального номера
        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи (тестовый)
    def start(self, gui_callback: GuiCallback):  # инъекция зависимосей 
        self.gui_callback = gui_callback         # для оповещения наблюдателя

        # запуск фоновой задачи (дальше перепишется через subprocess)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        TaskManager.reg_start(self)

    # поток задачи (тестовый)
    def run(self):
        for i in range(21):
            if self.stop_flag:
                return
            self.gui_callback.update(i/20)
            time.sleep(0.2)
        self.done = True
        TaskManager.reg_finish(self)
        self.gui_callback.finish(self.id)  # сигнал о завершении задачи

    # остановка задачи (тестовая)
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self.gui_callback.delete(self.id)  # сигнал о завершении задачи

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)  # сигнал об удалении задачи


class TaskManager:
    """Менеджер задач.
    Позволяет регистрировать задачи,
    и управлять ими."""

    _last_id: int = 0          # последний номер задачи
    _all_tasks: dict = {}      # словарь всех задач
    _running_tasks: dict = {}  # словарь активных задач

    @classmethod
    def create(cls, task_config: TaskConfig) -> Task:
        cls._last_id += 1  # увеличение последнего номера задачи
        unic_id = cls._last_id  # получение уникального номера

        task = Task(unic_id, task_config)  # создание задачи
        cls._reg(task)  # регистрация в менеджере
        return task

    # регистрация задачи
    @classmethod
    def _reg(cls, task: Task) -> None:
        cls._all_tasks[task.id] = task

    # регистрация запуска задачи
    @classmethod
    def reg_start(cls, task: Task) -> None:
        cls._running_tasks[task.id] = task

    # удаление регистрации запуска задачи
    @classmethod
    def reg_finish(cls, task: Task) -> None:
        if task.id in cls._running_tasks:
            cls._running_tasks.pop(task.id)

    # получение списка активных задач
    @classmethod
    def running_list(cls) -> list:
        return list(cls._running_tasks.values())

    # удаление задачи   
    @classmethod
    def wipe(cls, task: Task) -> None:
        cls.reg_finish(task)
        if task.id in cls._all_tasks:
            cls._all_tasks.pop(task.id)


    # получение списка всех задач
    @classmethod
    def all_list(cls) -> list:
        return list(cls._all_tasks.values())

    # проверка существования задачи    
    @classmethod
    def check(cls, task_id: int) -> bool:
        return task_id in cls._all_tasks
    




    #  из файла windows_base.py:

"""
Управление окнами происходит локальным менеджером окон.

Любое открытие окна происходит именно через него.
если окно уже прописано в его локальном словаре, 
оно не будет открыто повторно, будет возвращён его объект.

Если где угодно в коде нужно открыть/закрыть/сфокусировать
любое другое окно, через LocalWM можно получить его объект.
Также, можно получить список всех окон, например, для итерации.

WindowMixin - это абстрактный класс, от которого наследуются
все классы окон. В нём прописана базовая логика поведения окна.
Также, в нём есть инициализация стилей окна, и должны быть методы,
касающиеся пользовательских настроек, чтобы итерацией по всем окнам,
и вызове метода обновления для каждого окна, они применились везде.
К примеру, метод "update_texts" обновляет текст на всех виджетах окна.
"""



class LocalWM:
    """Класс для работы с окнами.
    Позволяет регистрировать окна,
    И управлять ими."""

    _all_windows: dict = {}  # общий словарь регистрации для окон

    # проверка, зарегистрировано ли окно
    @classmethod
    def check(cls, name: str) -> bool:
        return name in cls._all_windows

    # открытие окна
    @classmethod
    def open(cls, window_cls, name: str) -> Tk:    # принимает класс окна, имя окна
        if not cls.check('root'):                        # проверяем, есть ли корневое окно
            return cls._reg(window_cls(), 'root')        # регистрируем окно как корневое

        if not cls.check(name):                          # проверяем, зарегистрировано ли окно
            window = window_cls(root=cls.call('root'))   # создаём окно, передаём корневое окно
            cls._reg(window, name)                       # регистрируем окно
        return cls.call(name)
    

    # регистрация окна
    @classmethod
    def _reg(cls, window: Tk, name: str = None) -> None:
        if not name:  
            name = window.name
        if not cls.check(name):
            cls._all_windows[name] = window
        return window

    # получение окна
    @classmethod
    def call(cls, name: str) -> Optional[Tk]:
        if cls.check(name):
            return cls._all_windows[name]

    # удаление окна
    @classmethod
    def wipe(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows.pop(name)

    # получение списка всех окон
    @classmethod
    def all(cls) -> list:
        return list(cls._all_windows.values())
    
    # переключение фокуса на окно
    @classmethod
    def focus(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows[name].focus()

    # обновление открытых окон после завершения задачи
    @classmethod
    def update_on_task_finish(cls):
        if cls.check('warn') and not TaskManager.running_list():
            cls._all_windows['warn'].destroy()
            cls._all_windows.pop('warn')
        ...
    

class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    size: Tuple[int, int]   # размеры (ширина, высота) окна
    name: str               # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_style()     # настройка внешнего вида окна
        self._to_center()     # размещение окна в центре экрана
        self._init_widgets()  # создание виджетов
        self.update_texts()   # установка текста нужного языка
        self._pack_widgets()  # расстановка виджетов

    # закрытие окна
    def close(self) -> None:
        # удаляет регистрацию окна из менеджера
        LocalWM.wipe(self.name)
        self.destroy()  # закрывает окно

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Lang.read(f'{self.name}.title'))

        for w_name, widget in self.widgets.items():

            if w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                continue

            new_text_data = Lang.read(f'{self.name}.{w_name}')

            if w_name.startswith('cmb'): # если виджет это комбобокс
                widget.config(values=new_text_data)   
                widget.current(newindex=0)   
                continue    
            
            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:

        # если это побочное окно
        if isinstance(self, Toplevel):
            x = self.master.winfo_x() + self.master.winfo_width()/2 - self.size[0]/2  # размещаем по центру
            y = self.master.winfo_y() + self.master.winfo_height()/2 - self.size[1]/2  # главного окна

        # а если это главное окно    
        else:  # размещаем по центру экрана
            x = (self.winfo_screenwidth() - self.size[0]) / 2
            y = (self.winfo_screenheight() - self.size[1]) / 2

        self.geometry(f'+{int(x)}+{int(y)}')


    # настройка стиля окна, исходя из разрешения экрана
    def _set_style(self) -> None:

        # screen_height = self.winfo_screenheight()  # достаём высоту экрана
        # scale = (screen_height/540)                # индекс масштабирования
        # scale *= MAJOR_SCALING                     # домножаем на глобальную

        style=ttk.Style()
        # if TTK_THEME: style.theme_use(TTK_THEME)   # применение темы, если есть
        _font = font.Font(
            # family= "helvetica", 
            size=12, 
            weight='bold'
        )
        style.configure(style='.', font=_font)  # шрифт текста в кнопке
        self.option_add("*Font", _font)  # шрифты остальных виджетов

        # task_background = '#94d0eb'
        task_background = '#c4f0ff'
        style.configure('Task.TFrame', background=task_background)
        style.configure('Task.TLabel', background=task_background)
        style.configure('Task.Horizontal.TProgressbar', background=task_background)

        x, y = self.size                   # забираем объявленные размеры окна
        # x, y = int(x*scale), int(y*scale)  # масштабируем их
        self.geometry(f'{x}x{y}')          # и присваиваем их окну
        self.minsize(x, y)                 # и устанавливаем как минимальные
        try:
            x, y = self.size_max               # если есть максимальные размеры
            # x, y = int(x*scale), int(y*scale)  # масштабируем их
            self.maxsize(x, y)
        except AttributeError:
            pass



    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None:
        ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self, ) -> None:
        ...





    #  из файла windows_utils.py:

"""
Прокручиваемый фрейм это сложная структура, основанная на
объекте "холста", к которому крепятся полоса прокрутки и фрейм.
Далее следует большое количество взаимных подвязок, на разные случаи.

- если фрейм переполнен:
    ^ любые прокрутки невозможны

- полоса может прокручивать объект холста,
- при наведении мыши на холст, привязка возможностей:
    ^ колесо мыши может прокручивать холст и полосу прокрутки

Объект бара задачи это фрейм, в котором разные виджеты, относящиеся 
к описанию параметров задачи (картинка, лейблы для пути и параметров),
бар прогресса выполнения задачи, и кнопку отмены/удаления.
"""

# возвращает список всех изображений в директории
def find_img_in_dir(dir: str, full_path: bool = False) -> List[str]:
    img_list = [f for f in os.listdir(dir) if f.endswith(('.png', '.jpg'))]
    if full_path:
        img_list = list(map(lambda x: f'{dir}/{x}', img_list))  # добавляет путь к названию
    return img_list


# сокращает строку пути, расставляя многоточия внутри
def shrink_path(path: str, limit: int) -> str:
    if len(path) < limit:  # если длина и так меньше лимита
        return path

    # вычисление разделителя, добавление вначало, если нужно
    s = '/' if '/' in path else '\\'
    dirs = path.split(s)
    if path.startswith(s):
        dirs.pop(0)
        dirs[0] = s + dirs[0]

    # список укороченного пути, первый и последний элементы
    shrink = [dirs.pop(0), dirs.pop()] 
    while dirs and len(s.join(shrink) + dirs[-1]) + 4 < limit:  # если лимит не будет превышен,
        shrink.insert(1, dirs.pop())                            # добавить элемент с конца
    
    # сборка строки нового пути, передача её, если она короче изначальной
    new_path = f"{shrink[0]}{s}...{s}{s.join(shrink[1:])}"
    return new_path if len(new_path) < len(path) else path


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs)
        
        self.canvas = Canvas(self, highlightthickness=0)  # объект "холста"
        self.canvas.bind(           # привязка к виджету холста
            "<Configure>",          # обработчика событий, чтобы внутренний фрейм
            self._on_resize_window  # менял размер, если холст растягивается
            )

        self.scrollbar = ttk.Scrollbar(  # полоса прокрутки
            self, orient="vertical",     # установка в вертикальное положение
            command=self.canvas.yview,   # передача управления вертикальной прокруткой холста
        )  

        self.scrollable_frame = ttk.Frame(self.canvas, padding=[15, 0])  # фрейм для контента (внутренних виджетов)
        self.scrollable_frame.bind(  # привязка к виджету фрейма 
            "<Configure>",           # обработчика событий <Configure>, чтобы полоса
            self._update_scrollbar,  # прокрутки менялась, когда обновляется фрейм 
        )

        # привязка холста к верхнему левому углу, получение id фрейма
        self.frame_id = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw"
        )

        # передача управления полосы прокрутки, когда холст движется от колёсика
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # упаковка виджетов
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # привязка и отвязка событий, когда курсор заходит на холст
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

    # изменение размеров фрейма внутри холста
    def _on_resize_window(self, event):
        if event.width < 500:  # сюда залетают разные события
            return  # нас интересут только те, у которых ширина больше окна
        self.canvas.itemconfig(self.frame_id, width=event.width)  # новые размеры фрейма

    # обработка изменений полосы прокрутки
    def _update_scrollbar(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()

    # проверяет, нужна ли полоса прокрутки, и показывает/скрывает её
    def _update_scrollbar_visibility(self):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    # попытка активировать прокрутку колёсиком (если пройдёт валидацию)
    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._validate_mousewheel)

    # отвазать события прокрутки
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    # возможность прокрутки только если полоса активна, и фрейм переполнен
    def _validate_mousewheel(self, event):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class TaskBar(ttk.Frame):
    """Класс баров задач в основном окне"""

    def __init__(self, master: ttk.Frame, task: Task):
        super().__init__(master, borderwidth=1, padding=5, style='Task.TFrame')
        self.name = 'bar'
        self.widgets: Dict[str, Widget] = {}
        self.task: Task = task
        self.progress: float = 0

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # создание и настрйока виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        img_dir = self.task.config.get_dirs()[0]              # достаём первую директорию
        img_paths = find_img_in_dir(img_dir, full_path=True)  # берём все картинки из неё
        if len(img_paths) > 1:
            img_path = img_paths[len(img_paths)//2]           # выбираем центральную
        else:
            img_path = img_paths[0]

        image = Image.open(img_path)
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=image_tk)
        self.widgets['_picture'].image = image_tk


        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font=bigger_font, padding=5,
            text=shrink_path(self.task.config.get_filepath(), 32), 
            style='Task.TLabel'
        )

        # создание локализованых строк "качество: высокое | частота кадров: 50"
        quality_index = self.task.config.get_quality()
        quality = Lang.read('task.cmbQuality')[quality_index]
        quality_text = f"{Lang.read('task.lbQuality')} {quality}  |  "
        framerate_text = f"{Lang.read('task.lbFramerate')} {self.task.config.get_framerate()}"

        self.widgets['_lbData'] = ttk.Label(  
            self.mid_frame, 
            font='14', padding=5,
            text=quality_text+framerate_text, 
            style='Task.TLabel'
        )

        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5, style='Task.TFrame')
       
        # кнопка "отмена"
        self.widgets['btCancel'] = ttk.Button(self.right_frame, width=8, command=lambda: self.task.cancel())
        
        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.right_frame, 
            # length=320,
            maximum=1,
            value=0,
            style='Task.Horizontal.TProgressbar'
        )

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_picture'].pack(side='left')
        self.left_frame.pack(side='left')

        self.widgets['_lbPath'].pack(side='top', fill='x', expand=True)
        self.widgets['_lbData'].pack(side='top', fill='x', expand=True)
        self.mid_frame.pack(side='left')

        self.widgets['btCancel'].pack(side='bottom', expand=True)
        self.widgets['_progressBar'].pack(side='bottom', expand=True)
        self.right_frame.pack(side='left', expand=True)

        self.pack(pady=[0, 10])

    # обновление кнопки "отмена" после завершения задачи
    def update_cancel_button(self):
        self.widgets['btDelete'] = self.widgets.pop('btCancel')  # переименование кнопки
        self.widgets['btDelete'].config(
            command=lambda: self.task.delete(),  # переопределение поведения кнопки
        )
        self.update_texts()  # обновление текста виджетов

    # обновление линии прогресса
    def update_progress(self, progress: float, delta: bool = False):
        if delta:  # прогресс будет дополняться на переданное значение
            self.progress += progress
        else:  # прогресс будет принимать переданное значение
            self.progress = progress
        try:
            self.widgets['_progressBar'].config(value=self.progress)
        except:  # после удаления виджета вылетает ошибка из-за большой вложенности
            pass  # она ни на что не влияет, поэтому отлавливается и гасится

    # удаление бара
    def delete(self):
        self.destroy()

    # обновление текстов виджетов
    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))


class ImageCanvas(Canvas):
    """Объект холста с картинкой в окне создания задачи.
    на которой отображаются "умные" поля ввода.
    Если текст не введён - поле будет полупрозрачным."""
    
    def __init__(self, master: Tk, width: int, height: int, image_link: str = '', background: str = '#888888'):

        # создаёт объект холста
        super().__init__(master, width=width, height=height, highlightthickness=0, background=background)
        self.height, self.width = height, width
        self.pack()

        self.pil_img = None
        self.img = None
        self.img_id = None

        self.color = background
        self.alpha_square = None
        self._create_image(image_link)
        self._create_entries()

    # инициализация полупрозрачнях треугольников и полей ввода
    def _create_entries(self):

        self.entries = []                      # список всех полей ввода
        self.shown = [None for i in range(8)]  # список отображаемых на холсте полей
        self.labels = []
        self.alpha_squares = []

        # переменные для расположения виджетов
        x_pad = 120   # отступы по горизонтали
        y_pad = 50    # отступы по вертикали
        sq_size = 24  # размер прозр. квадрата

        # создание прозрачного квадрата
        self.alpha_square = self._create_alpha_square(sq_size, '#ffffff', 0.5)

        # 8 позиций и элементов на холсте, с левого верхнего по часовой стрелке
        positions = [
            (x_pad, y_pad),                            # верхний левый
            (self.width // 2, y_pad),                  # верхний
            (self.width - x_pad, y_pad),               # верхний правый
            (self.width - x_pad, self.height // 2),    # правый
            (self.width - x_pad, self.height - y_pad), # нижний правый
            (self.width // 2, self.height - y_pad),    # нижний
            (x_pad, self.height - y_pad),              # нижний левый
            (x_pad, self.height // 2),                 # левый
        ]

        # настройка и расположение значка "+" и виджета для каждой позиции
        for pos in positions:
            alpha_square = self.create_image(  # расположекние прозр. квадрата
                pos[0]-sq_size/2, 
                pos[1]-sq_size/2, 
                image=self.alpha_square, 
                anchor='nw'
            )
            label = self.create_text(pos[0], pos[1], text='+', font=("Arial", 24), justify='center')  # добавление текста
            entry = Entry(self, font=("Arial", 12), justify='center')  # инициализация поля ввода

            self.entries.append(entry) 
            self.labels.append(label)
            self.alpha_squares.append(alpha_square)
        
            # привязка события скрытия поля ввода, когда с него снят фокус
            entry.bind("<FocusOut>", lambda event, entry=entry: self._hide_entry(event, entry))

            # привязка события отображения поля ввода при нажатии на текст
            self.tag_bind(label, "<Button-1>", lambda event, pos=pos, entry=entry: self._show_entry(event, pos, entry))

    
    # создаёт картинку прозрачного квадрата
    def _create_alpha_square(self, size: int, fill: str, alpha: float):
        alpha = int(alpha * 255)
        fill = self.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (size, size), fill)
        return ImageTk.PhotoImage(image)

    # отображает поле ввода
    def _show_entry(self, event, pos, entry):
        index = self.entries.index(entry)
        entry_window = self.create_window(pos, window=entry, anchor=CENTER)
        self.shown[index] = entry_window
        entry.focus_set()

    # прячет поле ввода, меняет текст в лейбле
    def _hide_entry(self, event, entry):
        index = self.entries.index(entry)
        self.delete(self.shown[index])     # удаляет поле ввода
        self._update_label(index)

    # обновляет тексты лейблов и видимость квадрата
    def _update_label(self, index):
        label = self.labels[index]
        entry = self.entries[index]
        square = self.alpha_squares[index]

        text = '+'              # дефолтные значения, когда поле ввода пустое 
        font = ("Arial", 24)
        square_state = 'normal'
        label_color = 'black'

        if entry.get():  # если в поле ввода указан какой-то текст
            text = entry.get()       # этот текст будет указан в лейбле
            font = ("Arial", 16)     # шрифт будет поменьше
            square_state = 'hidden'  # полупрозрачный квадрат будет скрыт

            dark_background = self._is_dark_background(label)      # проверится, тёмный ли фон у тейбла
            label_color = 'white' if dark_background else 'black'  # если тёмный - шрифт светлый, и наоборот

        self.itemconfig(label, text=text, font=font, fill=label_color)  # придание тексту нужных параметров
        self.itemconfig(square, state=square_state)                     # скрытие или проявление квадрата

    # приобразование ссылки на картинку в объект
    def _open_image(self, image_link: str):
        try:
            pil_img = Image.open(image_link)               # открытие изображения по пути
            img_ratio = pil_img.size[0] / pil_img.size[1]  # оценка соотношения сторон картинки
            pil_img = pil_img.resize(
                (int(self.height*img_ratio), self.height), # масштабирование с учётом соотношения
                Image.LANCZOS
            )  
            self.pil_img = pil_img
            self.img = ImageTk.PhotoImage(pil_img)         # загрузка картинки и создание виджета

        except FileNotFoundError:                                           # если файл не найден
            self.img = ImageTk.PhotoImage(                                  # создаёт пустое изображение
                Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))  # с прозрачным фоном
            )

    # создание изображения
    def _create_image(self, image_link: str):
        self._open_image(image_link)
        self.img_id = self.create_image((self.width//2)-(self.img.width()//2), 0, anchor=NW, image=self.img)

        # привязка фокусировки на холст при нажатие на изображение, чтобы снять фокус с полей ввода
        self.tag_bind(self.img_id, "<Button-1>", lambda event: self.focus_set())

    # обновление изображения 
    def update_image(self, image_link: str):
        self._open_image(image_link)
        self.itemconfig(self.img_id, image=self.img)                            # замена изображения
        self.coords(self.img_id, (self.width // 2)-(self.img.width() // 2), 0)  # повторное задание координат
        for i in range(8):
            self._update_label(i)

    # проверка, тёмный ли фон на картинке за элементом канваса
    def _is_dark_background(self, elem_id: int) -> bool:
        try:
            image_shift = self.coords(self.img_id)[0]   # сдвиг картинки от левого края холста
            x, y = self.coords(elem_id)                 # координаты элемента на холсте
            x -= int(image_shift)                       # поправка, теперь это коорд. элемента на картинке
            if x < 0:
                raise IndexError                        # если координата меньше нуля

            color = self.pil_img.getpixel((x, y))       # цвет пикселя картинки на этих координатах
            r, g, b = color[0:3]
        except IndexError:                              # если пиксель за пределами картинки
            r, g, b = self.winfo_rgb(self.color)        # задний план будет оцениваться, исходя из
            r, g, b = r/255, g/255, b/255               # выбранного фона холста
        except TypeError:                       
            return color < 128                          # если pillow вернёт не ргб, а яркость пикселя
        
        brightness = (r*299 + g*587 + b*114) / 1000     # вычисление яркости пикселя по весам
        return brightness < 128                         # сравнение яркости

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        entries_text = map(lambda entry: entry.get(), self.entries)
        return list(entries_text)
    
    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.color = color
        self.config(background=color)


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории, 
    и менять порядок кнопками и перетаскиванием"""

    def __init__(self, master: Union[Tk, Frame]):
        super().__init__(master)
        self.name = 'dirs'

        self.dirs = []
        self.widgets: Dict[str, Widget] = {}
        self.drag_data = {"start_index": None, "item": None}

        self._init_widgets()
        self._pack_widgets()

    # возвращает список директорий
    def get_dirs(self) -> list:
        return self.dirs[:]
    
    def get_rand_img(self) -> Optional[str]:
        if not self.dirs: return

        rand_dir = random.choice(self.dirs)
        images = find_img_in_dir(rand_dir, full_path=True)
        if not images: return

        return random.choice(images)

    # подсветка виджета пути цветом предупреждения
    def _highlight_invalid_path(self, path_number: list):
        print(f'TODO подсветка несуществующего пути {path_number}')

    # подсветка кнопки добавления пути цветом предупреждения
    def _highlight_empty_path(self):
        print(f'TODO подсветка кнопки добавления пути')
    
    # проверка путей на валидность, передача в конфиг
    def validate_dirs(self) -> bool:
        if not self.dirs:
            self._highlight_empty_path()
            return False
        
        ok_flag = True  # вызовет подсветку несуществующих путей
        for i, dir in enumerate(self.dirs):
            if not os.path.isdir(dir):
                self._highlight_invalid_path(i)
                ok_flag = False

        return ok_flag

    # инициализация виджетов
    def _init_widgets(self):

        self.top_frame = Frame(self)

        self.widgets['lbDirList'] = ttk.Label(self.top_frame)  # надпись "Список директорий:"

        # создание списка и полосы прокрутки
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=28, height=4)
        self.scrollbar = ttk.Scrollbar(self.top_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.bind('<Button-1>', self._start_drag)
        self.listbox.bind('<B1-Motion>', self._do_drag)

        # добавление директории
        def add_directory():
            dir_name = filedialog.askdirectory(parent=self)
            if not dir_name or dir_name in self.dirs:
                return
            
            if not find_img_in_dir(dir_name):
                return

            self.listbox.insert(END, shrink_path(dir_name, 35))
            self.dirs.append(dir_name)  # добавление в список директорий

        # удаление выбранной директории из списка
        def remove_directory():
            selected = self.listbox.curselection()
            if selected:
                index = selected[0]
                self.listbox.delete(index)
                del self.dirs[index]

        self.button_frame = Frame(self)

        # создание кнопок для управления элементами списка
        self.widgets['btAddDir'] = ttk.Button(self.button_frame, width=8, command=add_directory)
        self.widgets['btRemDir'] = ttk.Button(self.button_frame, width=8, command=remove_directory)
        # self.widgets['btUpDir'] = ttk.Button(self.button_frame, width=2, text="^", command=self._move_up)
        # self.widgets['btDownDir'] = ttk.Button(self.button_frame, width=2, text="v", command=self._move_down)
    
    # начало перетаскивания элемента
    def _start_drag(self, event):
        self.drag_data["start_index"] = self.listbox.nearest(event.y)
        self.drag_data["item"] = self.listbox.get(self.drag_data["start_index"])

    def _swap_dirs(self, index_old: int, index_new: int, text: str = None):
        if not text:
            text = self.listbox.get(index_old)
        self.listbox.delete(index_old)
        self.listbox.insert(index_new, text)
        self.dirs[index_old], self.dirs[index_new] = self.dirs[index_new], self.dirs[index_old]

    # процесс перетаскивания элемента
    def _do_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_data["start_index"]:
            self._swap_dirs(self.drag_data["start_index"], new_index, self.drag_data["item"])
            self.drag_data["start_index"] = new_index

    # перемещение выбранной директории вверх по списку
    def _move_up(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                self._swap_dirs(index, index-1)
                self.listbox.select_set(index - 1)

    # перемещение выбранной директории вниз по списку
    def _move_down(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.listbox.size() - 1:
                self._swap_dirs(index, index+1)
                self.listbox.select_set(index + 1)

    # размещение виджетов
    def _pack_widgets(self):
        self.top_frame.pack(side='top', fill='x')
        self.widgets['lbDirList'].pack(side='top', anchor='w')
        self.listbox.pack(side='left', fill='x')
        self.scrollbar.pack(side='left', fill='y')


        self.button_frame.pack(side='top', anchor='w', pady=10)

        self.widgets['btAddDir'].pack(side='left', padx=(0, 10))
        self.widgets['btRemDir'].pack(side='right')
        # self.widgets['btUpDir'].pack(side='left')  # кнопки перетаскивания 
        # self.widgets['btDownDir'].pack(side='left') # вверх и вниз, пока убрал

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))






    #  из файла windows.py:

"""
Любое окно наследуется от Tk/TopLevel и WindowMixin.
Именно в таком порядке, это важно. Если перепутать, 
объект инициализируется как WindowMixin.

Вначале конструктора должен быть вызван super().__init__(),
который инициализирует объект как сущность Tk/TopLevel.

Должны быть объявлены имя окна, и необходимые атрибуты из миксина,
а в конце должен быть вызван метод super()._default_set_up().
Интерпретатор не найдёт такой метод в Tk/TopLevel, и будет 
выполнен метод из миксина.

Также, должны быть имплементированы методы создания и упаковки виджетов,
они тоже вызываются миксином при стандартной настройке окна. 

Любые виджеты внутри окна должны добавляться в словарь виджетов,
а тексты для них прописываться в классе языковых настроек Lang.
Если появляется более сложная композиция, метод update_texts должен
быть расширен так, чтобы вызывать обновление текста во всех виджетах.
"""


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name = 'root'
        
        self.widgets:   Dict[str, ttk.Widget] = {}
        self.task_bars: Dict[int, TaskBar] = {}  # словарь регистрации баров задач

        self.size = 550, 450
        self.size_max = 700, 700
        self.resizable(True, True)  # можно растягивать

        super()._default_set_up()

    # при закрытии окна
    def close(self):
        if TaskManager.running_list():  # если есть активные задачи
            # открытие окна с новой задачей (и/или переключение на него)
            return LocalWM.open(WarningWindow, 'warn').focus()
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):

        # открытие окна с новой задачей (и/или переключение на него)
        def open_new_task():
            LocalWM.open(NewTaskWindow, 'task').focus()

        # открытие окна настроек (и/или переключение на него)
        def open_settings():
            LocalWM.open(SettingsWindow, 'sets').focus()

        # создание фреймов
        self.upper_bar = upperBar = ttk.Frame(self)  # верхний бар с кнопками
        self.task_space = ScrollableFrame(self)  # пространство с прокруткой
        self.taskList = self.task_space.scrollable_frame  # сокращение пути для читаемости

        # создание виджетов, привязывание функций
        self.widgets['newTask'] = ttk.Button(upperBar, command=open_new_task)
        self.widgets['openSets'] = ttk.Button(upperBar, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.upper_bar.pack(fill='x', padx=15, pady=15)
        self.task_space.pack(fill='both', expand=True)

        self.widgets['newTask'].pack(side='left')
        self.widgets['openSets'].pack(side='right')
        
    # добавление строки задачи
    def add_task_bar(self, task: Task, **params) -> Callable:
        task_bar = TaskBar(self.taskList, task, **params)  # создаёт бар задачи
        self.task_bars[task.id] = task_bar  # регистрирует в словаре
        return task_bar.update_progress  # возвращает ручку полосы прогресса

    # удаление строки задачи
    def del_task_bar(self, task_id: int) -> None:
        self.task_bars[task_id].delete()  # удаляет таскбар
        del self.task_bars[task_id]  # чистит регистрацию

    # закрытие задачи, смена виджета
    def finish_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].update_cancel_button()
        LocalWM.update_on_task_finish()

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        for bar in self.task_bars.values():
            bar.update_texts()  # обновляет текст в каждом баре


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'sets'

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size = 250, 200
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):

        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['_cmbLang'].current())  # установка языка
            for w in LocalWM.all():  # перебирает все прописанные в менеджере окна
                w.update_texts()  # для каждого обновляет текст методом из WindowMixin

            ...  # считывание других виджетов настроек, и применение

        # сохранение настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()

        # создание виджетов, привязывание функций
        self.widgets['lbLang'] = ttk.Label(self)
        self.widgets['_cmbLang'] = ttk.Combobox(  # виджет выпадающего списка
            self,
            values=Lang.get_all(),  # вытягивает список языков
            state='readonly',  # запрещает вписывать, только выбирать
            width=7,
        )
        
        self.widgets['btApply'] = ttk.Button(self, command=apply_settings, width=7)
        self.widgets['btSave'] = ttk.Button(self, command=save_settings, width=7)

    # расположение виджетов
    def _pack_widgets(self):

        for c in range(2): 
            self.columnconfigure(index=c, weight=1)
        for r in range(5): 
            self.rowconfigure(index=r, weight=1)
        
        self.widgets['lbLang'].grid(row=0, column=0, sticky='w', padx=20)
        self.widgets['_cmbLang'].grid(row=0, column=1, sticky='ew', padx=(5 ,15))
        self.widgets['_cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык

        self.widgets['btApply'].grid(row=4, column=0, sticky='ew', padx=(15, 5), ipadx=30)
        self.widgets['btSave'].grid(row=4, column=1, sticky='ew', padx=(5, 15), ipadx=30)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets: Dict[str, Widget] = {}
        self.task_config = TaskConfig()

        self.size = 800, 650
        self.resizable(True, True)

        super()._default_set_up()
        self.image_updater_thread = threading.Thread(target=self.image_updater, daemon=True)
        self.image_updater_thread.start()

    # поток, обновляющий картинку на на холсте
    def image_updater(self):  
        try:
            while True:
                random_image = self.dir_manager.get_rand_img()
                if random_image:
                    self.image_canvas.update_image(image_link=random_image)
                time.sleep(2)
        except TclError:
            return

    # сбор данных из виджетов, создание конфигурации
    def _collect_task_config(self) -> None:
        overlays = self.image_canvas.fetch_entries_text()       # достаёт тексты оверлеев из виджетов,
        self.task_config.set_overlays(overlays_texts=overlays)  # передаёт их в конфиг задачи оверлеев.

        self.task_config.set_specs(
            framerate=self.widgets['_cmbFramerate'].get(),  # забирает выбранное значение в комбобоксе
            quality=self.widgets['cmbQuality'].current(),   # а в этом забирает индекс выбранного значения
        )
    
    # выбор пути для сохранения файла
    def _set_filepath(self) -> bool:
        filepath = filedialog.asksaveasfilename(
                parent=self,                                                # открытие окна сохранения файла
                filetypes=[("mp4 file", ".mp4"), ("webm file", ".webm")],   # доступные расширения и их имена
                defaultextension=".mp4"                                     # стандартное расширение
        )
        self.task_config.set_filepath(filepath)
        return bool(filepath)  # если путь выбран, вернёт true

    # создание и запуск задачи
    def _create_task_instance(self):

        # создание задачи через менеджер задач
        task = TaskManager.create(self.task_config)

        # создание бара задачи, получение метода обновления прогресса
        update_progress: Callable = self.master.add_task_bar(task)

        gui_callback = GuiCallback(                       # создание колбека
            update_function=update_progress,              # передача методов обновления,
            finish_function=self.master.finish_task_bar,  # завершения задачи
            delete_function=self.master.del_task_bar      # и удаления бара
        )

        task.start(gui_callback)  # инъекция колбека для обнволения gui при старте задачи

    # создание и настройка виджетов
    def _init_widgets(self):            
        self.image_canvas = ImageCanvas(  # создание холста с изображением
            self, 
            width=800, height=400,
            image_link="src/catframes/catmanager_sample/test_static/img.jpg", 
            background='#888888'
        )
        self.bottom_grid = Frame(self)    # создание табличного фрейма ниже холста
        self.dir_manager = DirectoryManager(self.bottom_grid)
        
        def add_task():  # обработка кнопки добавления задачи
            self._collect_task_config()   # сбор данных конфигурации с виджетов
            if not self.dir_manager.validate_dirs(): # если каких-то директорий нет,
                return                    # дальнейшие действия не произойдут
            
            dirs = self.dir_manager.get_dirs()
            self.task_config.set_dirs(dirs)

            if not self._set_filepath():  # если путь сохранения не выбирается,
                return                    # дальнейшие действия не произойдут
            self._create_task_instance()  # cоздание и запуск задачи
            self.close()                  # закрытие окна создания задачи

        def ask_color():  # вызов системного окна по выбору цвета
            color = colorchooser.askcolor(parent=self)[-1]
            self.image_canvas.update_background_color(color)
            self.task_config.set_color(color)  # установка цвета в конфиге
            self.widgets['_btColor'].configure(background=color, text=color)  # цвет кнопки

        # виджеты столбца описания кнопок
        self.widgets['lbColor'] = ttk.Label(self.bottom_grid)
        self.widgets['lbFramerate'] = ttk.Label(self.bottom_grid)
        self.widgets['lbQuality'] = ttk.Label(self.bottom_grid)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.widgets['_btColor'] = Button(self.bottom_grid, command=ask_color, text='#888888', width=7)
        self.widgets['_cmbFramerate'] = ttk.Combobox(  # виджет выбора фреймрейта
            self.bottom_grid,
            values=(60, 50, 40, 30, 25, 20, 15, 10, 5), 
            state='readonly',
            justify='center',
            width=8,
        )
        self.widgets['cmbQuality'] = ttk.Combobox(  # виджет выбора качества
            self.bottom_grid,
            state='readonly',
            justify='center',
            width=8,
        )
        self.widgets['btCreate'] = ttk.Button(self.bottom_grid, command=add_task)

    # расположение виджетов
    def _pack_widgets(self):
        # упаковка нижнего фрейма для сетки
        self.bottom_grid.pack(side='bottom', fill='both', expand=True, pady=10, padx=30)

        # настройка веса столбцов
        for i in range(4):
            self.bottom_grid.columnconfigure(i, weight=1)

        # настройка веса строк
        for i in range(6):
            self.bottom_grid.rowconfigure(i, weight=1)

        # заполнение левого столбца
        self.dir_manager.grid(
            row=0, column=0, rowspan=6, columnspan=2
        )

        # заполнение столбца описания кнопок (липнет вправо, к правому столбцу)        
        self.widgets['lbColor'].grid(row=1, column=2, sticky='e', padx=10)
        self.widgets['lbFramerate'].grid(row=2, column=2, sticky='e', padx=10)
        self.widgets['lbQuality'].grid(row=3, column=2, sticky='e', padx=10)

        # заполнение правого столбца (липнет влево, к столбцу описаний)
        ttk.Label(self.bottom_grid).grid(row=0, column=3)
        self.widgets['_btColor'].grid(row=1, column=3, sticky='w', padx=7)
        self.widgets['_cmbFramerate'].grid(row=2, column=3, sticky='w', padx=7)
        self.widgets['_cmbFramerate'].current(newindex=3)
        self.widgets['cmbQuality'].grid(row=3, column=3, sticky='w', padx=7)
        self.widgets['btCreate'].grid(row=4, column=3, sticky='w', padx=7)
        ttk.Label(self.bottom_grid).grid(row=5, column=3)

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()


class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'warn'
        self.widgets: Dict[str, Widget] = {}

        self.size = 260, 130
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        
        def back():
            self.close()

        def exit():
            print('TODO остановка всех задач')
            self.master.destroy()

        _font = font.Font(size=16)

        # два лейбла предупреждения (с крупным текстом, и обычным)
        self.widgets['lbWarn'] = ttk.Label(self, padding=[0, 20, 0, 5], font=_font)
        self.widgets['lbText'] = ttk.Label(self, padding=0)

        # кнопки "назад" и "выйти"
        self.choise_frame = ttk.Frame(self)
        self.widgets['btBack'] = ttk.Button(self.choise_frame, command=back)
        self.widgets['btExit'] = ttk.Button(self.choise_frame, command=exit)

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['lbWarn'].pack(side='top')
        self.widgets['lbText'].pack(side='top')

        self.widgets['btBack'].pack(side='left', anchor='w', padx=5)
        self.widgets['btExit'].pack(side='left', anchor='w', padx=5)
        self.choise_frame.pack(side='bottom', pady=10)





    #  из файла main.py:

def main():
    root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
    root.mainloop()

if __name__ == "__main__":
    main()


