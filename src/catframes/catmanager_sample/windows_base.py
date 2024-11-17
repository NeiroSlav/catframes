from _prefix import *
from sets_utils import Settings
from task_flows import TaskManager


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
    @classmethod  # принимает класс окна, имя окна
    def open(cls, window_cls, name: str, master: Optional[Tk] = None, **kwargs) -> Tk:

        # если корневого окна нет, то создаём и регистрируем
        if not cls.check("root"):
            return cls._reg(window_cls(), "root")

        if not master:
            master = cls.call("root")

        # если окно не зарегистрировано - создаёт его и регистрирует
        if not cls.check(name):
            window = window_cls(root=master, **kwargs)
            cls._reg(window, name)

        return cls.call(name)

    # регистрация окна
    @classmethod
    def _reg(cls, window: Tk, name: str = None) -> Tk:
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
        if cls.check("warn") and not TaskManager.running_list():
            cls._all_windows["warn"].destroy()
            cls._all_windows.pop("warn")


class MetaWindowMixin(ABCMeta):
    @staticmethod
    def check(a_field, a_type):
        if not isinstance(a_field, a_type):
            raise NotImplementedError("Missing attribute.")

    def __call__(cls, *args, **kwargs):
        instance = ABCMeta.__call__(cls, *args, **kwargs)

        cls.check(instance.title, Callable)
        cls.check(instance.protocol, Callable)
        cls.check(instance.destroy, Callable)

        cls.check(instance.size, tuple)
        cls.check(instance.size[0], int)
        cls.check(instance.size[1], int)

        cls.check(instance.name, str)
        cls.check(instance.widgets, dict)

        return instance


class WindowMixin(metaclass=MetaWindowMixin):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    # стандартная настройка окна, вызывается в конце конструктора
    def _default_set_up(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        if platform.system() == "Linux":
            self._set_linux_sizes()
        self._set_size()
        self._to_center()

        if self.name in ("root", "checker"):
            Settings.theme.lazy_init(master=self)
        self.after(1, self._init_widgets)
        self.after(2, self.update_texts)
        self.after(3, self._pack_widgets)

    # закрытие окна
    def close(self) -> None:
        LocalWM.wipe(self.name)
        self.destroy()

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Settings.lang.read(f"{self.name}.title"))

        for w_name, widget in self.widgets.items():

            # не применяется для виджетов, начинающихся с "_"
            if w_name.startswith("_"):
                continue

            new_text_data = Settings.lang.read(f"{self.name}.{w_name}")

            if w_name.startswith("cmb"):  # если виджет это комбобокс
                widget.config(values=new_text_data)
                widget.current(newindex=0)
                continue

            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:
        screen_size: tuple = (self.winfo_screenwidth(), self.winfo_screenheight())

        # если это не побочное окно, то размещаем по центру экрана
        if not isinstance(self, Toplevel):
            x = (screen_size[0] - self.size[0]) / 2
            y = (screen_size[1] - self.size[1]) / 2
            self.geometry(f"+{int(x)}+{int(y)}")
            return

        # далее для побочных окон:
        master_size = self.master.winfo_width(), self.master.winfo_height()
        master_coords = self.master.winfo_x(), self.master.winfo_y()

        x, y = self._calculate_coords(master_coords, master_size, self.size, screen_size)

        self.geometry(f"+{int(x)}+{int(y)}")

    @staticmethod
    def _calculate_coords(master_coords, master_size, window_size, screen_size) -> Tuple[int, int]:

        border_gap: int = 30  # минимальный отступ от края окна при открытии

        x = master_coords[0] + master_size[0] / 2 - window_size[0] / 2
        y = master_coords[1] + master_size[1] / 2 - window_size[1] / 2

        # далее описаны сценарии для случаев, когда новое окно,
        # при появлении, выходит за границы экрана

        if x < border_gap:
            x = border_gap

        if x + window_size[0] + border_gap > screen_size[0]:
            x = screen_size[0] - window_size[0] - border_gap

        if y < border_gap:
            y = border_gap

        # при выходе за нижнюю границу экрана, отсуп больше
        if y + window_size[1] + (border_gap * 3) > screen_size[1]:
            y = screen_size[1] - window_size[1] - (border_gap * 3)

        return int(x), int(y)

    def _set_linux_sizes(self):
        x, y = self.size
        self.size = int(x*LINUX_SIZING), int(y*LINUX_SIZING)

        if hasattr(self, "size_max"):
            x, y = self.size_max
            self.size_max = int(x*LINUX_SIZING), int(y*LINUX_SIZING)

    def _set_size(self):
        x, y = self.size
        self.geometry(f"{x}x{y}")
        self.minsize(x, y)

        if hasattr(self, "size_max"):
            self.maxsize(*self.size_max)

    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None: ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self) -> None: ...


class TextDialog(Toplevel, WindowMixin):
    """Показывает произвольный текст с прокруткой без возможности его редактирования."""

    def __init__(self, root: Tk, window_name: str, text: str):
        super().__init__(master=root)
        self.name = window_name
        self.text = text

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size = 650, 300
        self.resizable(False, False)
        self.transient(root)

        # Сокрытие при анфокусе скопировано из SettingsWindow.
        self.bind("<FocusOut>", self._on_focus_out)

        super()._default_set_up()

    def _set_style(self) -> None:
        super()._set_style()
        self.minsize(200, 150)

    def _init_widgets(self):
        self.main_frame = Frame(self)
        self.non_localized_text = scrolledtext.ScrolledText(self.main_frame, padx=10, pady=10)
        self.non_localized_text.insert(END, self.text + '\n')
        self.non_localized_text['state'] = 'disabled'

    def _pack_widgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        self.non_localized_text.pack(side=TOP, fill=BOTH, expand=True)

    def _on_focus_out(self, event):
        if not self.focus_get():
            return self.close()
