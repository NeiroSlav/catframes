from _prefix import *
from templog import has_console, compiled


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

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        "english": {
            "root.title": "Catmanager",
            "root.openSets": "Settings",
            "root.newTask": "Create",
            "bar.active": "processing",
            "bar.inactive": "complete",
            "bar.btInfo": "Info",
            "bar.btCancel": "Cancel",
            "bar.btDelete": "Delete",
            "bar.lbEmpty": "Your projects will appear here",
            "bar.error.noffmpeg": "Error! FFmpeg not found!",
            "bar.error.nocatframes": "Error! Catframes not found!",
            "bar.error.internal": "Internal process error!",
            "bar.error.failed": "Error! Process start failed!",
            "bar.lbQuality": "Quality:",
            "bar.lbFramerate": "Framerate:",
            "bar.lbColor": "Color:",
            "sets.title": "Settings",
            "sets.lbLang": "Language:",
            "sets.lbTheme": "Theme:",
            "sets.btApply": "Apply",
            "sets.btSave": "Save",
            "sets.btOpenLogs": "Show logs",
            "task.title": "New Task",
            "task.title.view": "Task settings view",
            "task.initText": "Add a directory\nof images",
            "task.lbColor": "Background:",
            "task.lbFramerate": "Framerate:",
            "task.lbQuality": "Quality:",
            "task.cmbQuality": ("high", "medium", "poor"),
            "task.lbResolution": "Render resolution:",
            "task.lbSaveAs": "Save as:",
            "task.btCreate": "Create",
            "task.btPathChoose": "choose",
            "task.lbCopy": "Copy cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 sec", "2 sec", "3 sec", "4 sec", "5 sec"),
            "task.btPrevCancel": "Cancel",
            "task.lbPrevSign": "Processing preview...",
            "dirs.lbDirList": "List of source directories:",
            "dirs.btAddDir": "Add",
            "dirs.btRemDir": "Remove",
            "dirs.DirNotExists": "Doesn't exists. Removing...",
            "warn.exit.title": "Warning",
            "warn.exit.lbWarn": "Warning!",
            "warn.exit.lbText": "Incomplete tasks!",
            "warn.exit.btAccept": "Leave",
            "warn.exit.btDeny": "Back",
            "warn.cancel.title": "Warning",
            "warn.cancel.lbWarn": "Are you sure",
            "warn.cancel.lbText": "You want to cancel the task?",
            "warn.cancel.btAccept": "Yes",
            "warn.cancel.btDeny": "Back",
            "about.title": "About application",
            "about.appTab": "About App",
            "about.storyTab": "Story",
            "about.copyMail": "Copy",
            "about.btMail": "Email",
            "about.btSite": "Website",
            "about.txtName": "Name",
            "about.txtNameContent": f"Catmanager ({platform.machine()})",
            "about.txtDesc": "Description",
            "about.txtDescContent": "Graphical interface for Catframes",
            "about.txtLicense": "License",
            "about.txtLicenseContent": "zlib (libpng)",
            "about.txtVersion": "Version",
            "about.txtVersionContent": RELEASE_VERSION,
            "about.txtAbout": (
                "Catframes is a program for combining frames into videos. \n"
                "It chooses the correct resolution to avoid losing the clarity of most frames, "
                "and does not distort the proportions while zooming."
            ),
            "checker.title": "Necessary modules check",

            "emptyFolder.title": "Empty folder",
            "emptyFolder.theFollowingFolders": "The following folders do not contain images.\nTherefore, they were not added.",
        },
        "русский": {
            "root.title": "Catmanager",
            "root.openSets": "Настройки",
            "root.newTask": "Создать",
            "bar.lbActive": "обработка",
            "bar.lbInactive": "завершено",
            "bar.btInfo": "Инфо",
            "bar.btCancel": "Отмена",
            "bar.btDelete": "Удалить",
            "bar.lbEmpty": "Здесь появятся Ваши проекты",
            "bar.error.noffmpeg": "Ошибка! FFmpeg не найден!",
            "bar.error.nocatframes": "Ошибка! Catframes не найден!",
            "bar.error.internal": "Внутренняя ошибка процесса!",
            "bar.error.failed": "Ошибка при старте процесса!",
            "bar.lbQuality": "Качество:",
            "bar.lbFramerate": "Частота:",
            "bar.lbColor": "Цвет:",
            "sets.title": "Настройки",
            "sets.lbLang": "Язык:",
            "sets.lbTheme": "Тема:",
            "sets.btApply": "Применить",
            "sets.btSave": "Сохранить",
            "sets.btOpenLogs": "Показать логи",
            "task.title": "Новая задача",
            "task.title.view": "Просмотр настроек задачи",
            "task.initText": "Добавьте папку\nс изображениями",
            "task.lbColor": "Цвет фона:",
            "task.lbFramerate": "Частота кадров:",
            "task.lbQuality": "Качество:",
            "task.cmbQuality": ("высокое", "среднее", "низкое"),
            "task.lbResolution": "Разрешение рендера:",
            "task.lbSaveAs": "Сохранить как:",
            "task.btCreate": "Создать",
            "task.btPathChoose": "выбрать",
            "task.lbCopy": "Копировать cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 сек", "2 сек", "3 сек", "4 сек", "5 сек"),
            "task.btPrevCancel": "Отмена",
            "task.lbPrevSign": "Создание предпросмотра...",
            "dirs.lbDirList": "Список директорий источников:",
            "dirs.btAddDir": "Добавить",
            "dirs.btRemDir": "Удалить",
            "dirs.DirNotExists": "Не существует. Удаление...",
            "warn.exit.title": "Внимание",
            "warn.exit.lbWarn": "Внимание!",
            "warn.exit.lbText": "Задачи не завершены!",
            "warn.exit.btAccept": "Выйти",
            "warn.exit.btDeny": "Назад",
            "warn.cancel.title": "Внимание",
            "warn.cancel.lbWarn": "Вы уверены,",
            "warn.cancel.lbText": "Что хотите отменить задачу?",
            "warn.cancel.btAccept": "Да",
            "warn.cancel.btDeny": "Назад",
            "about.title": "О программе",
            "about.appTab": "Программа",
            "about.storyTab": "История",
            "about.copyMail": "Копировать",
            "about.btMail": "Эл-почта",
            "about.btSite": "Веб-сайт",
            "about.txtName": "Название",
            "about.txtNameContent": f"Catmanager ({platform.machine()})",
            "about.txtDesc": "Описание",
            "about.txtDescContent": "Графический интерфейс для Catframes",
            "about.txtLicense": "Лицензия",
            "about.txtLicenseContent": "zlib (libpng)",
            "about.txtVersion": "Версия",
            "about.txtVersionContent": RELEASE_VERSION,
            "about.txtAbout": (
                "Catframes - это программа для объединения кадров в видеоролики. \n"
                "Она сама выбирает разрешение, чтобы избежать потери чёткости большинства кадров, "
                "и не искажает пропорции при масштабировании."
            ),
            "checker.title": "Проверка необходимых модулей",

            "emptyFolder.title": "Пустая директория",
            "emptyFolder.theFollowingFolders": "Следующие папки не были добавлены, т.к. не содержат изображений.",
        },
        "中文": {
            "root.title": "Catmanager",
            "root.openSets": "设置",
            "root.newTask": "开始创建",
            "bar.lbActive": "处理过程",
            "bar.lbInactive": "已完成",
            "bar.btInfo": "资料",
            "bar.btCancel": "取消",
            "bar.btDelete": "删除",
            "bar.lbEmpty": "您的项目将出现在这里",
            "bar.error.noffmpeg": "搞错了！ 没有找到FFmpeg！",
            "bar.error.nocatframes": "搞错了！ 没有找到Catframes！",
            "bar.error.internal": "内部进程错误！",
            "bar.error.failed": "过程开始时出错！",
            "bar.lbQuality": "图像质量:",
            "bar.lbFramerate": "频率:",
            "bar.lbColor": "颜色:",
            "sets.title": "设置",
            "sets.lbLang": "语言:",
            "sets.lbTheme": "设计的主题:",
            "sets.btApply": "保存设置",
            "sets.btSave": "保存设置",
            "sets.btOpenLogs": "显示日志",
            "task.title": "一项新任务",
            "task.title.view": "查看任务设置",
            "task.initText": "添加包含图\n像的文件夹",
            "task.lbColor": "背景颜色:",
            "task.lbFramerate": "帧速率:",
            "task.lbQuality": "图像质量:",
            "task.cmbQuality": ("高品质", "平均质量", "低质量"),
            "task.lbResolution": "渲染分辨率:",
            "task.lbSaveAs": "文件保存路径:",
            "task.btCreate": "开始创建",
            "task.btPathChoose": "选择文件路径",
            "task.lbCopy": "复制命令行:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 秒", "2 秒", "3 秒", "4 秒", "5 秒"),
            "task.btPrevCancel": "取消",
            "task.lbPrevSign": "创建预览。..",
            "dirs.lbDirList": "源目录列表:",
            "dirs.btAddDir": "添加",
            "dirs.btRemDir": "移走",
            "dirs.DirNotExists": "目录不存在。 移走..",
            "warn.exit.title": "注意",
            "warn.exit.lbWarn": "注意！",
            "warn.exit.lbText": "还有未完成的任务!",
            "warn.exit.btAccept": "离开程序",
            "warn.exit.btDeny": "返回程序",
            "warn.cancel.title": "注意",
            "warn.cancel.lbWarn": "您确定",
            "warn.cancel.lbText": "要取消任务吗？",
            "warn.cancel.btAccept": "确认",
            "warn.cancel.btDeny": "返回程序",
            "about.title": "有关计算机程序的信息",
            "about.appTab": "计算机程序",
            "about.storyTab": "发展历史",
            "about.copyMail": "副本",
            "about.btMail": "电邮",
            "about.btSite": "网站",
            "about.txtName": "程序的名称",
            "about.txtNameContent": f"Catmanager ({platform.machine()})",
            "about.txtDesc": "程序描述",
            "about.txtDescContent": "Catframes 的图形界面",
            "about.txtLicense": "程序许可证",
            "about.txtLicenseContent": "zlib (libpng)",
            "about.txtVersion": "程序版本",
            "about.txtVersionContent": RELEASE_VERSION,
            "about.txtAbout": (
                "Catframes是一个将帧组合成视频的程序。\n",
                "她自己选择分辨率，以避免失去大多数帧的清晰度，\n",
                "并且在缩放时不会扭曲比例。"
            ),
            "checker.title": "检查必要的模块",

            "emptyFolder.title": "空目录",
            "emptyFolder.theFollowingFolders": "以下文件夹未添加，因为它们不包含图像。",
        },
    }

    def __init__(self):
        self.current_name = "english"
        self.current_index = 0

    # получение всех доступных языков
    def get_all(self) -> tuple:
        return tuple(self.data.keys())

    # установка языка по имени или индексу
    def set(self, name: str = None, index: int = None) -> None:

        if name and name in self.data:
            self.current_index = self.get_all().index(name)
            self.current_name = name

        elif isinstance(index, int) and 0 <= index < len(self.data):
            self.current_name = self.get_all()[index]
            self.current_index = index

    # получение текста по тегу
    def read(self, tag: str) -> Union[str, tuple]:
        try:
            return self.data[self.current_name][tag]
        except KeyError:  # если тег не найден
            return "-----"


class Theme:
    """Класс настроек ttk темы"""

    master: Tk
    style: ttk.Style
    data: tuple
    current_name: str
    current_index: int

    # вызывается после создания главного окна
    def lazy_init(self, master: Tk):
        self.master = master
        self.style = ttk.Style()
        self.data = self.style.theme_names()
        self.set()

    def set_name(self, name: str):
        self.current_name = name

    def get_all(self):
        return self.data

    def set(self, index: Optional[int] = None):
        if not hasattr(self, "master"):
            return

        if index == None:
            self.current_index = self.data.index(self.current_name)
        else:
            self.current_name = self.data[index]
            self.current_index = index

        self.style.theme_use(self.current_name)
        self.set_styles()

        _font = font.Font(size=12)
        self.style.configure(style=".", font=_font)  # шрифт текста в кнопке
        self.master.option_add("*Font", _font)  # шрифты остальных виджетов

    def set_styles(self):
        self.style.configure("Main.TaskList.TFrame", background=MAIN_TASKLIST_COLOR)
        self.style.configure("Main.ToolBar.TFrame", background=MAIN_TOOLBAR_COLOR)

        # создание стилей фона таскбара для разных состояний
        for status, color in MAIN_TASKBAR_COLORS.items():
            self.style.configure(f"{status}.Task.TFrame", background=color)
            self.style.configure(f"{status}.Task.TLabel", background=color)
            self.style.configure(
                f"{status}.Task.Horizontal.TProgressbar", background=color
            )

        self.style.map(
            "Create.Task.TButton",
            background=[("active", "blue"), ("!disabled", "blue")],
        )


class UtilityLocator:
    """Ищет утилиты в системе по имени"""

    def __init__(self):
        self.use_ffmpeg_from_system_path: bool = False
        self.use_catframes_from_system_path: bool = False

        self.ffmpeg_full_path: Union[str, None] = None
        self.catframes_full_path: Union[str, None] = None

        self.catframes_command_memo: Union[List[str], None] = None

    def set_ffmpeg(self, is_in_sys_path: bool, full_path: str):
        self.use_ffmpeg_from_system_path = is_in_sys_path
        self.ffmpeg_full_path = full_path

    def set_catframes(self, is_in_sys_path: bool, full_path: str):
        self.use_catframes_from_system_path = is_in_sys_path
        self.catframes_full_path = full_path

    def find_ffmpeg(self) -> Union[str, None]:
        self.use_ffmpeg_from_system_path = self.find_in_sys_path('ffmpeg')
        self.ffmpeg_full_path = self.find_full_path('ffmpeg', self.use_ffmpeg_from_system_path)
        return self.ffmpeg_full_path

    def find_catframes_command(self) -> List[str]:
        if self.catframes_command_memo:
            return self.catframes_command_memo.copy()

        logger = logging.getLogger('catmanager')
        windows = (platform.system() == 'Windows')

        ran_from_sources: bool = ('main.py' == Path(sys.argv[0]).name)

        if ran_from_sources:
            catframes_py: Path = Path(sys.argv[0]).resolve().parent.parent / 'catframes.py'
        else:
            catframes_py: Path = Path(sys.argv[0]).resolve().parent / 'catframes.py'

        catframes_exe: Path = Path(sys.argv[0]).resolve().parent / 'catframes.exe'

        # Здесь не используется sys.executable напрямую,
        # поскольку там может быть pythonw.exe.
        python_exe: Path = Path(sys.executable).resolve().parent / 'python.exe'

        logger.debug(f'\n               windows: {windows}')
        logger.debug(f'              compiled: {compiled()}')
        logger.debug(f'      ran from sources: {ran_from_sources}')
        logger.debug(f'          catframes_py: {catframes_py}')
        logger.debug(f'         catframes_exe: {catframes_exe}')
        logger.debug(f'            python_exe: {python_exe}\n')

        logger.debug(f'   catframes_py exists: {catframes_py.exists()}')
        logger.debug(f'  catframes_exe exists: {catframes_exe.exists()}')
        logger.debug(f'     python_exe exists: {python_exe.exists()}\n')

        if windows and not compiled() and catframes_py.exists():
            logger.info('Using local catframes.py (Windows)')
            logger.info(f'Python executable: {python_exe}')
            command = [str(python_exe), str(catframes_py)]
        elif windows and compiled() and catframes_exe.exists():
            logger.info('Using local catframes.exe')
            command = [str(catframes_exe)]
        elif not compiled() and catframes_py.exists() and shutil.which('python'):
            logger.info('Using local catframes.py (POSIX)')
            logger.info(f'Python executable: python')
            command = ['python', str(catframes_py)]
        elif not compiled() and catframes_py.exists() and shutil.which('python3'):
            logger.info('Using local catframes.py (POSIX)')
            logger.info(f'Python executable: python3')
            command = ['python3', str(catframes_py)]
        else:
            logger.info('Using Catframes from PATH.')
            command = ["catframes"]

        self.catframes_command_memo = command
        return command.copy()

    def find_catframes(self) -> Union[str, None]:
        command: List[str] = self.find_catframes_command()

        if (["catframes"] == command) and not shutil.which(command[0]):
            return None

        return " ".join(command)

    # ищет полный путь для утилиты
    # если она есть в path, то ищет консолью
    @staticmethod
    def find_full_path(utility_name: str, is_in_sys_path: bool) -> Optional[str]:
        if is_in_sys_path:
            return shutil.which(utility_name)

        paths_to_check = UtilityLocator._get_paths(utility_name)
        for path in paths_to_check:
            if os.path.isfile(path):
                return path

    # возвращает пути, по которым может быть утилита, исходя из системы
    @staticmethod
    def _get_paths(utility_name: str) -> List[str]:
        system = platform.system()

        if system == "Windows":
            return [
                os.path.join(
                    os.environ.get("ProgramFiles", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
                os.path.join(
                    os.environ.get("ProgramFiles(x86)", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
            ]
        elif system == "Linux":
            return [
                "/usr/bin/" + utility_name,
                "/usr/local/bin/" + utility_name,
            ]
        elif system == "Darwin":
            return [
                "/usr/local/bin/" + utility_name,
                "/opt/homebrew/bin/" + utility_name,
            ]

    # проверка, есть ли утилита в системном path
    @staticmethod
    def find_in_sys_path(utility_name) -> bool:
        try:
            result = subprocess.run(
                [utility_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output = ''
            for i in range(3):
                output += result.stderr.decode()
            if result.returncode == 0 or ("usage" in output):
                return True
        except FileNotFoundError:
            pass
        return False


class IniConfig:
    """Создание, чтение, и изменение внешнего файла конфига"""

    def __init__(self):
        self.file_path = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)
        self.file_exists = os.path.isfile(self.file_path)
        self.config = configparser.ConfigParser()

        if self.file_exists:
            self.config.read(self.file_path)
        else:
            self.set_default()

    # создание стандартного конфиг файла
    def set_default(self):
        self.config["Settings"] = {
            "Language": "english",
            "UseSystemPath": "yes",
            "TtkTheme": "vista" if platform.system() == "Windows" else "default",
        }
        self.config["AbsolutePath"] = {
            "FFmpeg": "",
        }
        self.config["SystemPath"] = {
            "FFmpeg": "",
        }

    # редактирование ключа в секции конфиг файла
    def update(self, section: str, key: str, value: Union[str, int]):
        if section in self.config:
            self.config[section][key] = value

    def save(self):
        with open(self.file_path, "w") as configfile:
            self.config.write(configfile)
        self.file_exists = True


class Settings:
    """Содержит объекты всех классов настроек"""

    lang = Lang()
    theme = Theme()
    util_locatior = UtilityLocator()
    conf = IniConfig()

    @classmethod
    def save(cls):
        cls.conf.update("Settings", "Language", str(cls.lang.current_index))
        cls.conf.update("Settings", "TtkTheme", cls.theme.current_name)
        cls.conf.save()

    @classmethod
    def restore(cls):

        # поддержка старого формата .ini файлов, где язык был словом, а не индексом
        try:
            cls.lang.set(index=int(cls.conf.config["Settings"]["Language"]))
        except ValueError:
            cls.lang.set(name=cls.conf.config["Settings"]["Language"])

        cls.theme.set_name(cls.conf.config["Settings"]["TtkTheme"])
        cls.util_locatior.set_ffmpeg(
            is_in_sys_path=cls.conf.config["SystemPath"]["FFmpeg"]=='yes',
            full_path=cls.conf.config["AbsolutePath"]["FFmpeg"]
        )
