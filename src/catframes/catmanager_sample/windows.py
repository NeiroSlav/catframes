from _prefix import *
from sets_utils import Settings
from windows_utils import *
from task_flows import Task, GuiCallback, TaskManager, TaskConfig
from windows_base import WindowMixin, LocalWM
from templog import TempLog


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
а тексты для них прописываться в классе настроек Settings, в атрибуте lang.
Если появляется более сложная композиция, метод update_texts должен
быть расширен так, чтобы вызывать обновление текста во всех виджетах.
"""


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name: str = "root"

        self.widgets: Dict[str, ttk.Widget] = {}
        self.task_bars: Dict[int, TaskBar] = {}  # словарь регистрации баров задач

        # TODO: исправить тип
        self.size: Tuple[int] = 550, 450
        self.resizable(True, True)  # можно растягивать

        super()._default_set_up()

    # при закрытии окна
    def close(self):

        def accept_uncomlete_exit():
            for task in TaskManager.running_list():
                task.cancel()
            self.destroy()

        if TaskManager.running_list():  # если есть активные задачи
            # открытие окна с новой задачей (и/или переключение на него)
            return LocalWM.open(
                WarningWindow,
                name="warn",
                master=self,
                type="exit",
                accept_def=accept_uncomlete_exit,
            ).focus()
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):
        logger = logging.getLogger('catmanager')

        # открытие окна с новой задачей (и/или переключение на него)
        def open_new_task():
            LocalWM.open(NewTaskWindow, "task").focus()

        # открытие окна настроек (и/или переключение на него)
        def open_settings():
            LocalWM.open(SettingsWindow, "sets").focus()

        # создание фреймов
        self.upper_bar = upperBar = ttk.Frame(self, style="Main.ToolBar.TFrame")
        self.task_space = ScrollableFrame(self)
        self.taskList = self.task_space.scrollable_frame

        # создание виджетов, привязывание функций
        self.widgets["newTask"] = ttk.Button(upperBar, command=open_new_task)
        self.widgets["openSets"] = ttk.Button(upperBar, command=open_settings)

        logger.info('Root window started.')

    # расположение виджетов
    def _pack_widgets(self):
        self.upper_bar.pack(fill=X)
        self.task_space.pack(fill=BOTH, expand=True)

        self.widgets["newTask"].pack(side=LEFT, padx=10, pady=10)
        self.widgets["openSets"].pack(side=RIGHT, padx=10, pady=10)

    # добавление строки задачи
    def add_task_bar(self, task: Task, **params) -> Callable:
        # сборка функции для открытия диалога при попытке отмены задачи
        cancel_def = lambda: LocalWM.open(WarningWindow, "warn", self, type="cancel", accept_def=task.cancel)
        task_bar = TaskBar(self.taskList, task, cancel_def=cancel_def, **params)
        self.task_bars[task.id] = task_bar
        return task_bar.update_progress  # возвращает ручку полосы прогресса

    # удаление строки задачи
    def del_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].delete()
            del self.task_bars[task_id]

    # обработка ошибки процесса catframes
    def handle_error(self, task_id: int, error: str) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].set_error(error)
        LocalWM.update_on_task_finish()

    # закрытие задачи, смена виджета
    def finish_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].finish()
        LocalWM.update_on_task_finish()

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        for bar in self.task_bars.values():
            bar.update_texts()


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name: str = "sets"

        self.widgets: Dict[str, ttk.Widget] = {}

        # TODO: исправить тип
        self.size: Tuple[int] = 250, 150
        self.resizable(False, False)
        self.transient(root)

        self.bind("<FocusOut>", self._on_focus_out)

        super()._default_set_up()

    # при потере фокуса окна, проверяет, не в фокусе ли его виджеты
    def _on_focus_out(self, event):
        try:
            if not self.focus_get():
                return self.close()
        except:  # ловит ошибку, которая возникает при фокусе на комбобоксе
            pass

    # создание и настройка виджетов
    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.content_frame = ttk.Frame(self.main_frame)

        # виджет и комбобокс языка
        self.widgets["lbLang"] = ttk.Label(self.content_frame)
        self.widgets["_cmbLang"] = ttk.Combobox(
            self.content_frame,
            values=Settings.lang.get_all(),  # вытягивает список языков
            state="readonly",
            width=9,
        )

        def open_logs():
            log_paths = TempLog.get_paths()
            if (log_paths is not None) and ('catmanager' in log_paths):
                log_file_path = Path(log_paths['catmanager'])
                logs_path = str(log_file_path.parent)
                my_system = platform.system()

                if my_system == 'Windows':
                    subprocess.run(['explorer', logs_path])
                elif my_system == 'Linux':
                    subprocess.run(['xdg-open', logs_path])
                elif my_system == 'Darwin':
                    subprocess.run(['open', '--', logs_path])

        self.widgets['btOpenLogs'] = ttk.Button(self.main_frame, command=open_logs)

        # виджет и комбобокс тем
        self.widgets["lbTheme"] = ttk.Label(self.content_frame)
        self.widgets["_cmbTheme"] = ttk.Combobox(
            self.content_frame,
            values=ttk.Style().theme_names(),
            state="readonly",
            width=9,
        )

        # применение настроек
        def apply_settings(event):
            current_theme = self.widgets["_cmbTheme"].current()
            Settings.theme.set(index=current_theme)
            current_lang = self.widgets["_cmbLang"].current()
            Settings.lang.set(index=current_lang)
            Settings.save()

            for window in LocalWM.all():
                window.update_texts()

        # привязка применения настроек к выбору нового значения в комбобоксах
        self.widgets["_cmbLang"].bind("<<ComboboxSelected>>", apply_settings)
        self.widgets["_cmbTheme"].bind("<<ComboboxSelected>>", apply_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.content_frame.pack(padx=10, pady=30)

        self.widgets["lbLang"].grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbLang"].grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbLang"].current(
            newindex=Settings.lang.current_index
        )  # подставляем в ячейку текущий язык

        self.widgets["lbTheme"].grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbTheme"].grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbTheme"].current(newindex=Settings.theme.current_index)
        self.widgets['btOpenLogs'].grid(row=1, column=0, sticky='e', padx=5, pady=10)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name: str = "task"
        self.widgets: Dict[str, Widget] = {}

        self.task_config: TaskConfig = TaskConfig()
        self.view_mode: bool = False

        # если передан конфиг, берёт его, устанавливает флаг просмотра
        if kwargs.get("task_config"):
            self.task_config = kwargs.get("task_config")
            self.view_mode = True

        # TODO: исправить тип
        self.size: Tuple[int] = 900, 500

        # Временный хак.
        # У дефолтной страшненькой темы Tk в Линуксе виджеты больше по высоте,
        # и все кнопки не влезают в 500 пикселей.
        if 'Linux' == platform.system():
            self.size = 900, 620

        self.resizable(True, True)

        super()._default_set_up()
        threading.Thread(target=self.canvas_updater, daemon=True).start()

    def close(self):
        super().close()

        # удаляет директорию с превью рендерами
        dir_path = os.path.join(USER_DIRECTORY, PREVIEW_DIRNAME)
        if not os.path.exists(dir_path):
            return
        for i in range(10):
            try:
                shutil.rmtree(dir_path)
                break
            except:
                time.sleep(1)

    # поток, обновляющий картинку и размеры холста
    def canvas_updater(self):
        last_dirs = []
        images_to_show = []
        image_index = 0

        # проверяет, не поменялся ли список картинок
        def check_images_change():
            nonlocal images_to_show, last_dirs, image_index

            new_dirs = self.dir_manager.get_dirs()
            if last_dirs == new_dirs:
                return

            last_dirs = new_dirs
            all_images = self.dir_manager.get_all_imgs()

            # если картинок меньше 4, забираем все
            if len(all_images) < 4:
                images_to_show = all_images
                image_index = 0
            else:  # если их много - выбираем с нужным шагом
                step = len(all_images) // 4
                images_to_show = all_images[step::step]

        # попытка обновления картинки
        def update_image():
            nonlocal image_index

            if not images_to_show:
                self.image_canvas.clear_image()
                return

            self.image_canvas.update_image(images_to_show[image_index])
            image_index = (image_index + 1) % len(images_to_show)
            time.sleep(10)

        while True:
            try:
                check_images_change()
                update_image()
                time.sleep(1)
            except AttributeError:
                time.sleep(0.1)
            except TclError:  # это исключение появится, когда окно закроется
                return

    # сбор данных из виджетов, создание конфигурации
    def _collect_task_config(self):
        overlays_texts = self.image_canvas.fetch_entries_text()
        self.task_config.set_overlays(overlays_texts=overlays_texts)

        framerate = self.widgets["_spnFramerate"].get()
        quality = self.widgets["cmbQuality"].current()
        self.task_config.set_specs(framerate=framerate, quality=quality)

    # проверяет, указаны ли директории и путь сохранения файла
    # если нет - кнопки копирования, сохранения, предпросмотра будут недоступны
    def _validate_task_config(self):
        state = "disabled"
        if self.task_config.get_dirs() and self.task_config.get_filepath():
            state = "enabled"

        self.widgets["btCopyBash"].configure(state=state)
        self.widgets["btCopyWin"].configure(state=state)
        self.widgets["cmbTime"].configure(
            state=state if state == "disabled" else "readonly"
        )
        self.widgets["_btPreview"].configure(state=state)
        self.widgets["btCreate"].configure(state=state)

    # создание и запуск задачи
    def _create_task_instance(self):
        task: Task = TaskManager.create(self.task_config)

        # создание бара задачи, получение метода обновления прогресса
        update_progress: Callable = self.master.add_task_bar(
            task, view=NewTaskWindow.open_view
        )
        # передача всех методов в объект коббека,
        # и инъекция его при старте задачи
        gui_callback = GuiCallback(
            update_function=update_progress,
            finish_function=self.master.finish_task_bar,
            error_function=self.master.handle_error,
            delete_function=self.master.del_task_bar,
        )
        task.start(gui_callback)

    @staticmethod
    def _watch_preview(link: str):
        time.sleep(3)
        os.startfile(link)

    @staticmethod
    def _create_temp_dir():
        dir_path = os.path.join(USER_DIRECTORY, PREVIEW_DIRNAME)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # создаёт копию конфига, но с параметрами для превью
    def _create_preview_config(self) -> TaskConfig:
        preview_config = copy.deepcopy(self.task_config)
        self._create_temp_dir()
        extention = preview_config.get_filepath().split(".")[-1]
        preview_path = os.path.join(
            USER_DIRECTORY, PREVIEW_DIRNAME, PREVIEW_FILENAME.format(ex=extention)
        )
        limit = self.widgets["cmbTime"].current() + 1
        preview_config.set_preview_params(limit=limit, path=preview_path)
        return preview_config

    # создание и запуск задачи
    def _create_task_preview(self):
        # для создания задачи под рендеринг превью,
        # в коллбек передаются адапторы,
        # влияющие на полосу прогресса, и её отмену

        config: TaskConfig = self._create_preview_config()
        task: Task = TaskManager.create(config)
        self.widgets["btPrevCancel"].configure(command=task.cancel)

        def updating_adapter(progress: float, *args, **kwargs):
            try:
                self.widgets["_prevProgress"].config(value=progress)
            except:
                task.cancel()

        def deletion_adapter(*args, **kwargs):
            self._cancel_processing_screen()

        def finishing_adapter(*args, **kwargs):
            if not task.stop_flag:
                self._watch_preview(config.get_filepath())
            self._cancel_processing_screen()

        def handle_error(id, error):
            print(f"ошибка {error}")

        gui_callback = GuiCallback(
            update_function=updating_adapter,
            finish_function=finishing_adapter,
            error_function=handle_error,
            delete_function=deletion_adapter,
        )
        task.start(gui_callback)


    # Валидация для поля ввода цвета
    # Должна пропускать любые 16-р значения
    # до 6ти знаков, с "#" вначале и без.
    # Пустая строка допустима.
    @staticmethod
    def validate_color(value: str) -> bool:
        if not value:
            return True
        if value.count("#") > 1:
            return False
        if value.count("#") == 1 and not value.startswith("#"):
            return False
        value = value.lstrip("#")
        if len(value) > 6:
            return False
        for v in value:
            if v.lower() not in "0123456789abcdef":
                return False
        return True

    # Валидация для поля ввода фпс.
    # Должна пропускать любые числа от 0 до 60.
    # Пустая строка так же допустима.
    @staticmethod
    def validate_fps(value) -> bool:
        if not value:
            return True
        if not value.isdigit():
            return False
        return 0 <= int(value) <= 60

    def _init_widgets(self):
        self.main_frame = Frame(self)
        self.main_pane = PanedWindow(
            self.main_frame,
            orient=HORIZONTAL,
            sashwidth=5,
            background="grey",
            sashrelief="flat",
            opaqueresize=True,
            proxybackground="grey",
            proxyborderwidth=5,
            proxyrelief="flat",
        )

        # создание холста с изображением
        self.canvas_frame = Frame(self.main_pane, background=DEFAULT_CANVAS_COLOR)
        self.main_pane.add(self.canvas_frame, stretch="always")
        self.main_pane.paneconfig(self.canvas_frame, minsize=300)
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.config(width=self.winfo_width() - 200)

        self.image_canvas = ImageCanvas(
            master=self.canvas_frame,
            veiw_mode=self.view_mode,
            overlays=self.task_config.get_overlays(),
            background=self.task_config.get_color(),
        )

        # создание табличного фрейма меню
        self.menu_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.menu_frame, stretch="never")
        self.main_pane.paneconfig(self.menu_frame, minsize=250)

        self._bind_resize_events()

        # передача дитекротий в конфиг, валидация
        def set_dirs_to_task_config(dirs):
            self.task_config.set_dirs(dirs)
            self._validate_task_config()

        self.dir_manager = DirectoryManager(
            master=self.menu_frame,
            veiw_mode=self.view_mode,
            dirs=self.task_config.get_dirs(),
            on_change=set_dirs_to_task_config,  # передача ручки
        )
        self.settings_grid = ttk.Frame(self.menu_frame)

        # выбор пути для сохранения файла
        def ask_filepath():
            filetypes = [("mp4 file", ".mp4"), ("webm file", ".webm")]
            filepath = filedialog.asksaveasfilename(
                parent=self,
                filetypes=filetypes,
                defaultextension=".mp4",
                initialdir=GlobalStates.last_dir,
            )
            if filepath:
                GlobalStates.last_dir = os.path.dirname(filepath)
                self.task_config.set_filepath(filepath)
                self.widgets["_btPath"].configure(text=filepath.split("/")[-1])
                self._validate_task_config()

        # виджеты столбца описания кнопок
        self.widgets["lbColor"] = ttk.Label(self.settings_grid)
        self.widgets["lbFramerate"] = ttk.Label(self.settings_grid)
        self.widgets["lbQuality"] = ttk.Label(self.settings_grid)
        self.widgets["lbSaveAs"] = ttk.Label(self.settings_grid)

        # передача цвета в холст и конфиг
        def update_color(color: str):
            self.image_canvas.update_background_color(color)
            self.canvas_frame.config(background=color)
            self.task_config.set_color(color)

        # вызов системного окна по выбору цвета
        def ask_color():
            color = colorchooser.askcolor(parent=self)[-1]
            if not color:
                return
            self.widgets["_entColor"].delete(0, END)
            self.widgets["_entColor"].insert(0, color)
            update_color(color)

        self.color_frame = ttk.Frame(self.settings_grid)


        v_color = self.register(self.validate_color), "%P"

        self.widgets["_entColor"] = ttk.Entry(
            self.color_frame,
            validate="key",
            validatecommand=v_color,
            justify=CENTER,
            width=5,
        )
        self.widgets["_entColor"].insert(0, self.task_config.get_color())

        def check_empty_color(event):
            text: str = self.widgets["_entColor"].get()
            self.widgets["_entColor"].delete(0, END)

            if text.startswith("#"):
                text = text.lower().lstrip("#")
            if len(text) == 0:
                self.widgets["_entColor"].insert(0, DEFAULT_CANVAS_COLOR)
                return

            missing = 6 - len(text)
            color = "#" + text + "0" * missing
            self.widgets["_entColor"].insert(0, color)
            update_color(color)

        self.widgets["_entColor"].bind("<FocusOut>", check_empty_color)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.palette_icon = PhotoImage(data=base64.b64decode(PALETTE_ICON_BASE64))
        self.widgets["_btColor"] = ttk.Button(
            self.color_frame,
            command=ask_color,
            image=self.palette_icon,
            compound=CENTER,
            width=2,
        )


        v_fps = self.register(self.validate_fps), "%P"

        self.widgets["_spnFramerate"] = ttk.Spinbox(  # виджет выбора фреймрейта
            self.settings_grid,
            from_=1,
            to=60,
            validate="key",
            validatecommand=v_fps,
            justify=CENTER,
            width=8,
        )

        # проверяет, пустое ли поле ввода, и если да, вписывает минимальное значиние
        def check_empty_fps(event):
            value = self.widgets["_spnFramerate"].get()
            value = int(value) if value else 1
            value = value or 1
            self.widgets["_spnFramerate"].set(value)

        self.widgets["_spnFramerate"].bind("<FocusOut>", check_empty_fps)

        self.widgets[
            "_spnFramerate"
        ].set(  # установка начального значения в выборе фреймрейта
            self.task_config.get_framerate()
        )

        self.widgets["cmbQuality"] = ttk.Combobox(  # виджет выбора качества
            self.settings_grid,
            state="readonly",
            justify=CENTER,
            width=8,
        )

        path = self.task_config.get_filepath()
        file_name = (
            path.split("/")[-1] if path else Settings.lang.read("task.btPathChoose")
        )
        self.widgets["_btPath"] = ttk.Button(
            self.settings_grid, command=ask_filepath, text=file_name
        )
        ToolTip(self.widgets["_btPath"], self.task_config.get_filepath)

        # копирование команды в буфер обмена
        def copy_to_clip(bash: bool = True):
            self._collect_task_config()
            command = self.task_config.convert_to_command(for_user=True, bash=bash)
            command = " ".join(command)
            self.clipboard_clear()
            self.clipboard_append(command)

        # лейбл и кнопка копирования команды
        self.widgets["lbCopy"] = ttk.Label(self.settings_grid)
        self.copy_frame = ttk.Frame(self.settings_grid)
        self.widgets["btCopyBash"] = ttk.Button(
            self.copy_frame, command=copy_to_clip, width=3
        )
        self.widgets["btCopyWin"] = ttk.Button(
            self.copy_frame, command=lambda: copy_to_clip(bash=False), width=3
        )

        # если это режим просмотра, все виджеты, кроме копирования будут недоступны
        if self.view_mode:
            for w_name, w in self.widgets.items():
                if "lb" in w_name or "Copy" in w_name:
                    continue
                w.configure(state="disabled")

        self.create_frame = ttk.Frame(self.settings_grid)

        self.widgets["cmbTime"] = ttk.Combobox(
            self.create_frame,
            state="readonly",
            values=Settings.lang.read("task.cmbTime"),
            justify=CENTER,
            width=6,
        )
        self.play_icon = PhotoImage(data=base64.b64decode(PLAY_ICON_BASE64))
        self.widgets["_btPreview"] = ttk.Button(
            self.create_frame,
            command=self._show_processing_screen,
            image=self.play_icon,
            compound=CENTER,
            width=2,
        )

        def add_task():
            self._collect_task_config()
            self._create_task_instance()
            self.close()

        self.widgets["btCreate"] = ttk.Button(
            self.create_frame, command=add_task, style="Create.Task.TButton", width=8
        )

        # далее объявляются виджеты экрана рендера предпросмотра
        self.preview_outer_frame = ttk.Frame(self)
        self.preview_inner_frame = ttk.Frame(self.preview_outer_frame)

        self.widgets["lbPrevSign"] = ttk.Label(
            self.preview_inner_frame,
            font=font.Font(size=14),
        )
        self.widgets["_prevProgress"] = ttk.Progressbar(
            self.preview_inner_frame,
            length=320,
            maximum=1,
            value=0,
        )
        self.widgets["btPrevCancel"] = ttk.Button(
            self.preview_inner_frame,
            command=self._cancel_processing_screen,
            text="cancel",
        )

    def _show_processing_screen(self):
        try:
            self.main_frame.pack_forget()
            self.preview_outer_frame.pack(expand=True, fill=BOTH)
            self._collect_task_config()
            self._create_task_preview()
        except TclError:
            pass

    def _cancel_processing_screen(self):
        try:
            self.main_frame.pack(expand=True, fill=BOTH)
            self.preview_outer_frame.pack_forget()
        except TclError:
            pass

    # привязка событий изменений размеров
    def _bind_resize_events(self):
        """ресайз картинки - это долгий процесс, PIL задерживает поток,
        поэтому, во избежание лагов окна - логика следующая:

        если пользователь всё ещё тянет окно/шторку -
            холст меняет расположение оверлеев

        но если события изменения не было уже 100мс -
            холст обновляет размер всего, в том числе - картинки"""

        resize_delay = 100  # задержка перед вызовом обновления
        resize_timer = None  # идентификатор таймера окна

        def trigger_update(resize_image: bool):
            new_width = self.canvas_frame.winfo_width()
            new_height = self.canvas_frame.winfo_height()
            self.image_canvas.update_resolution(new_width, new_height, resize_image)

        # вызов при любом любом изменении размера
        def on_resize(event):

            # если событие - изменение размера окна,
            # но ширина или высота меньше минимальных,
            # то его обрабатывать не нужно
            if event.type == 22:
                if event.width < self.size[0] or event.height < self.size[1]:
                    return

            nonlocal resize_timer
            trigger_update(resize_image=False)

            if resize_timer:
                self.after_cancel(resize_timer)

            # новый таймер, который вызовет обновление через заданное время
            resize_timer = self.after(resize_delay, trigger_update, True)

        # привязка обработчика к событиям
        # изменения размеров окна и перетягиания шторки
        self.bind("<Configure>", on_resize)
        self.main_pane.bind("<Configure>", on_resize)

    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.main_pane.pack(expand=True, fill=BOTH)

        self.dir_manager.pack(expand=True, fill=BOTH, padx=(15, 0), pady=(20, 0))
        self.settings_grid.pack(fill=X, pady=10, padx=10)

        self.settings_grid.columnconfigure(0, weight=0)
        self.settings_grid.columnconfigure(1, weight=1)

        self.widgets["lbColor"].grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.color_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_entColor"].pack(side=LEFT, fill=X, expand=True)
        self.widgets["_btColor"].pack(side=LEFT)

        self.widgets["lbFramerate"].grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_spnFramerate"].grid(
            row=1, column=1, sticky="sewn", padx=5, pady=5
        )

        self.widgets["lbQuality"].grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.widgets["cmbQuality"].grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.widgets["lbSaveAs"].grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_btPath"].grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.widgets["lbCopy"].grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.copy_frame.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.widgets["btCopyBash"].pack(side=LEFT, fill=BOTH, expand=True)
        self.widgets["btCopyWin"].pack(side=LEFT, fill=BOTH, expand=True)

        if not self.view_mode:
            self.create_frame.grid(
                columnspan=2, row=5, column=0, sticky="e", padx=5, pady=(15, 5)
            )
            self.widgets["btCreate"].pack(padx=(10, 0), side=RIGHT)
            self.widgets["_btPreview"].pack(side=RIGHT)
            self.widgets["cmbTime"].pack(side=RIGHT)

        self._validate_task_config()

        # далее пакуются виджеты экрана рендера предпросмотра
        self.preview_outer_frame.grid_columnconfigure(0, weight=1)
        self.preview_outer_frame.grid_rowconfigure(0, weight=1)

        self.preview_inner_frame.grid(row=0, column=0, sticky="")
        self.widgets["lbPrevSign"].pack(anchor="nw")
        self.widgets["_prevProgress"].pack(pady=10)
        self.widgets["btPrevCancel"].pack(anchor="se")

    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()
        self.image_canvas.update_texts()

        # установка начального значения в выборе качества
        self.widgets["cmbQuality"].current(newindex=self.task_config.get_quality())
        if self.view_mode:
            self.title(Settings.lang.read(f"task.title.view"))
        if not self.task_config.get_filepath():
            self.widgets["_btPath"].configure(
                text=Settings.lang.read("task.btPathChoose")
            )

    # открытие окна в режиме просмотра
    @staticmethod
    def open_view(task_config: TaskConfig):
        LocalWM.open(NewTaskWindow, "task", task_config=task_config)


class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name = "warn"
        self.type: str = kwargs.get("type")
        self.accept_def: Callable = kwargs.get("accept_def")

        self.widgets: Dict[str, Widget] = {}
        self.size = 260, 150
        self.resizable(False, False)

        super()._default_set_up()

    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)

        # два лейбла предупреждения (с крупным текстом, и обычным)
        self.widgets["lbWarn"] = ttk.Label(
            self.main_frame, padding=[0, 20, 0, 5], font=font.Font(size=16)
        )
        self.widgets["lbText"] = ttk.Label(self.main_frame, padding=0)

        # кнопки "назад" и "выйти"
        self.choise_frame = ttk.Frame(self.main_frame)

        def accept():
            self.accept_def()
            self.close()

        self.widgets["btAccept"] = ttk.Button(self.choise_frame, command=accept)
        self.widgets["btDeny"] = ttk.Button(self.choise_frame, command=self.close)

    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)

        self.widgets["lbWarn"].pack(side=TOP)
        self.widgets["lbText"].pack(side=TOP)

        self.widgets["btAccept"].pack(side=LEFT, anchor="w", padx=5)
        self.widgets["btDeny"].pack(side=LEFT, anchor="w", padx=5)
        self.choise_frame.pack(side=BOTTOM, pady=10)

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            new_text_data = Settings.lang.read(f"{self.name}.{self.type}.{w_name}")
            widget.config(text=new_text_data)


class NotifyWindow(Toplevel, WindowMixin):
    """Окно предупреждения о портах в настройках"""

    def __init__(self, root: Toplevel):
        super().__init__(master=root)
        self.name: str = "noti"
        self.widgets: Dict[str, Widget] = {}

        self.size: Tuple[int] = 350, 160
        self.resizable(False, False)

        super()._default_set_up()

    def _init_widgets(self):

        _font = font.Font(size=16)

        self.widgets["lbWarn"] = ttk.Label(self, padding=[0, 20, 0, 5], font=_font)
        self.widgets["lbText"] = ttk.Label(self, padding=0)
        self.widgets["lbText2"] = ttk.Label(self, padding=0)

        self.frame = ttk.Frame(self)
        self.widgets["_btOk"] = ttk.Button(self.frame, text="OK", command=self.close)

    def _pack_widgets(self):
        self.widgets["lbWarn"].pack(side=TOP)
        self.widgets["lbText"].pack(side=TOP)
        self.widgets["lbText2"].pack(side=TOP)

        self.widgets["_btOk"].pack(anchor="w", padx=5)
        self.frame.pack(side=BOTTOM, pady=10)
