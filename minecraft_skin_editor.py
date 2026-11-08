import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
import numpy as np
import os
import random

class MinecraftSkinEditor:
    def __init__(self, root):
        self.root = root
        
        # НЕ используем overrideredirect - оставляем стандартную рамку Windows
        # Это гарантирует, что окно останется в панели задач при минимизации
        self.root.attributes('-topmost', False)  # Не всегда поверх
        
        # Получаем реальный размер экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Размер окна - полный экран минус панель задач Windows
        window_width = screen_width
        window_height = screen_height - 40  # 40px для панели задач
        
        # Позиция - в верхний левый угол
        self.root.geometry(f"{window_width}x{window_height}+0+0")
        self.root.title("🎮 Minecraft Skin Editor Pro")
        
        # Современная цветовая палитра - приятная для глаз
        self.colors = {
            'bg_dark': '#1e1e2e',          # Темный фон
            'bg_medium': '#2a2d3a',        # Средний фон
            'bg_light': '#3a3f51',         # Светлый фон
            'accent': '#7289da',           # Discord blue (приятный)
            'accent_hover': '#5b6eae',     # Темнее для hover
            'success': '#43b581',          # Зеленый
            'warning': '#faa61a',          # Оранжевый
            'danger': '#f04747',           # Красный
            'text': '#dcddde',             # Светло-серый текст
            'text_secondary': '#72767d',   # Серый текст
            'panel': '#2f3136',            # Панели
            'panel_hover': '#36393f',      # Hover панелей
            'titlebar': '#202225',         # Title bar
            'button_primary': '#5865f2',   # Основная кнопка
            'button_secondary': '#4f545c'  # Вторичная кнопка
        }
        
        # Устанавливаем темную тему
        self.setup_modern_style()
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Текущий скин
        self.current_skin = None
        self.skin_size = 64  # По умолчанию стандартный размер
        self.skin_photo = None
        
        # Текущий плащ
        self.current_cape = None
        self.cape_enabled = False
        self.cape_size = 64  # По умолчанию стандартный размер плаща
        
        # Переменные UI
        self.size_var = tk.StringVar(value="64x64")
        self.cape_var = tk.BooleanVar()
        self.multi_mode = tk.StringVar(value="individual")
        self.image_pool = []
        self.body_tree = None
        self.selection_info = None
        
        # Области скина (координаты для 64x64) - полная карта скина
        self.skin_regions = {
            # Голова (основной слой)
            "head_front": (8, 8, 16, 16),
            "head_back": (24, 8, 32, 16),
            "head_right": (0, 8, 8, 16),
            "head_left": (16, 8, 24, 16),
            "head_top": (8, 0, 16, 8),
            "head_bottom": (16, 0, 24, 8),
            
            # Голова (второй слой - шляпа/аксессуары)
            "head_overlay_front": (40, 8, 48, 16),
            "head_overlay_back": (56, 8, 64, 16),
            "head_overlay_right": (32, 8, 40, 16),
            "head_overlay_left": (48, 8, 56, 16),
            "head_overlay_top": (40, 0, 48, 8),
            "head_overlay_bottom": (48, 0, 56, 8),
            
            # Тело (основной слой)
            "body_front": (20, 20, 28, 32),
            "body_back": (32, 20, 40, 32),
            "body_right": (16, 20, 20, 32),
            "body_left": (28, 20, 32, 32),
            "body_top": (20, 16, 28, 20),
            "body_bottom": (28, 16, 36, 20),
            
            # Тело (второй слой - куртка)
            "body_overlay_front": (20, 36, 28, 48),
            "body_overlay_back": (32, 36, 40, 48),
            "body_overlay_right": (16, 36, 20, 48),
            "body_overlay_left": (28, 36, 32, 48),
            "body_overlay_top": (20, 32, 28, 36),
            "body_overlay_bottom": (28, 32, 36, 36),
            
            # Правая рука (основной слой)
            "arm_right_front": (44, 20, 48, 32),
            "arm_right_back": (52, 20, 56, 32),
            "arm_right_right": (40, 20, 44, 32),
            "arm_right_left": (48, 20, 52, 32),
            "arm_right_top": (44, 16, 48, 20),
            "arm_right_bottom": (48, 16, 52, 20),
            
            # Правая рука (второй слой - рукав)
            "arm_right_overlay_front": (44, 36, 48, 48),
            "arm_right_overlay_back": (52, 36, 56, 48),
            "arm_right_overlay_right": (40, 36, 44, 48),
            "arm_right_overlay_left": (48, 36, 52, 48),
            "arm_right_overlay_top": (44, 32, 48, 36),
            "arm_right_overlay_bottom": (48, 32, 52, 36),
            
            # Левая рука (основной слой)
            "arm_left_front": (36, 52, 40, 64),
            "arm_left_back": (44, 52, 48, 64),
            "arm_left_right": (32, 52, 36, 64),
            "arm_left_left": (40, 52, 44, 64),
            "arm_left_top": (36, 48, 40, 52),
            "arm_left_bottom": (40, 48, 44, 52),
            
            # Левая рука (второй слой - рукав)
            "arm_left_overlay_front": (52, 52, 56, 64),
            "arm_left_overlay_back": (60, 52, 64, 64),
            "arm_left_overlay_right": (48, 52, 52, 64),
            "arm_left_overlay_left": (56, 52, 60, 64),
            "arm_left_overlay_top": (52, 48, 56, 52),
            "arm_left_overlay_bottom": (56, 48, 60, 52),
            
            # Правая нога (основной слой)
            "leg_right_front": (4, 20, 8, 32),
            "leg_right_back": (12, 20, 16, 32),
            "leg_right_right": (0, 20, 4, 32),
            "leg_right_left": (8, 20, 12, 32),
            "leg_right_top": (4, 16, 8, 20),
            "leg_right_bottom": (8, 16, 12, 20),
            
            # Правая нога (второй слой - штанина)
            "leg_right_overlay_front": (4, 36, 8, 48),
            "leg_right_overlay_back": (12, 36, 16, 48),
            "leg_right_overlay_right": (0, 36, 4, 48),
            "leg_right_overlay_left": (8, 36, 12, 48),
            "leg_right_overlay_top": (4, 32, 8, 36),
            "leg_right_overlay_bottom": (8, 32, 12, 36),
            
            # Левая нога (основной слой)
            "leg_left_front": (20, 52, 24, 64),
            "leg_left_back": (28, 52, 32, 64),
            "leg_left_right": (16, 52, 20, 64),
            "leg_left_left": (24, 52, 28, 64),
            "leg_left_top": (20, 48, 24, 52),
            "leg_left_bottom": (24, 48, 28, 52),
            
            # Левая нога (второй слой - штанина)
            "leg_left_overlay_front": (4, 52, 8, 64),
            "leg_left_overlay_back": (12, 52, 16, 64),
            "leg_left_overlay_right": (0, 52, 4, 64),
            "leg_left_overlay_left": (8, 52, 12, 64),
            "leg_left_overlay_top": (4, 48, 8, 52),
            "leg_left_overlay_bottom": (8, 48, 12, 52)
        }
        
        # Области плаща (координаты для 64x64)
        self.cape_regions = {
            "cape_back": (1, 1, 11, 17),      # Задняя часть плаща
            "cape_front": (12, 1, 22, 17),    # Передняя часть плаща (внутренняя)
            "cape_right": (0, 1, 1, 17),      # Правая сторона
            "cape_left": (11, 1, 12, 17),     # Левая сторона
            "cape_top": (1, 0, 11, 1),        # Верх плаща
            "cape_bottom": (11, 0, 21, 1)     # Низ плаща
        }
        
        self.setup_ui()
        self.create_default_skin()
        self.setup_skin_tree()  # Инициализируем дерево после создания UI
        
    def setup_modern_style(self):
        """Настраивает современный стиль интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Общие настройки
        style.configure('.', 
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['bg_medium'],
                       borderwidth=0)
        
        # Фреймы
        style.configure('TFrame', 
                       background=self.colors['bg_dark'],
                       relief='flat')
        
        style.configure('Panel.TFrame',
                       background=self.colors['panel'],
                       relief='flat',
                       borderwidth=2)
        
        # LabelFrame - панели с заголовками
        style.configure('TLabelframe',
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       borderwidth=2,
                       relief='flat')
        
        style.configure('TLabelframe.Label',
                       background=self.colors['panel'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Кнопки
        style.configure('TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('Segoe UI', 9, 'bold'))
        
        style.map('TButton',
                 background=[('active', self.colors['accent_hover']),
                            ('pressed', self.colors['bg_light'])],
                 foreground=[('active', 'white')])
        
        # Вторичные кнопки
        style.configure('Secondary.TButton',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'])
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['panel_hover'])],
                 foreground=[('active', self.colors['accent'])])
        
        # Кнопки инструментов (иконки)
        style.configure('Tool.TButton',
                       background=self.colors['panel'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 16),
                       padding=(10, 10))
        
        style.map('Tool.TButton',
                 background=[('active', self.colors['accent']),
                            ('pressed', self.colors['accent_hover'])],
                 foreground=[('active', 'white')])
        
        # Checkbutton
        style.configure('TCheckbutton',
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))
        
        style.map('TCheckbutton',
                 background=[('active', self.colors['panel'])],
                 foreground=[('active', self.colors['accent'])])
        
        # Radiobutton
        style.configure('TRadiobutton',
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))
        
        style.map('TRadiobutton',
                 background=[('active', self.colors['panel'])],
                 foreground=[('selected', self.colors['accent'])])
        
        # Labels
        style.configure('TLabel',
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 9))
        
        style.configure('Title.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Accent.TLabel',
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Treeview
        style.configure('Treeview',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['bg_medium'],
                       borderwidth=0,
                       font=('Segoe UI', 9))
        
        style.configure('Treeview.Heading',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.map('Treeview.Heading',
                 background=[('active', self.colors['accent_hover'])])
        
        # Scrollbar
        style.configure('Vertical.TScrollbar',
                       background=self.colors['panel'],
                       troughcolor=self.colors['bg_medium'],
                       borderwidth=0,
                       arrowsize=13)
        
        style.map('Vertical.TScrollbar',
                 background=[('active', self.colors['accent'])])
    
    def setup_ui(self):
        # Используем стандартный titlebar Windows для надежной работы с панелью задач
        # Настраиваем заголовок окна
        self.root.title("🎮 MINECRAFT SKIN EDITOR PRO v2.0")
        
        # Привязываем обработчики событий для синхронизации плавающих окон
        self.root.bind('<Unmap>', self.on_minimize)  # Когда окно минимизируется
        self.root.bind('<Map>', self.on_restore)      # Когда окно восстанавливается
        
        # Главный фрейм с градиентом
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Левая панель - компактная панель инструментов
        self.tool_panel = tk.Frame(main_frame, bg=self.colors['panel'], width=70)
        self.tool_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.tool_panel.pack_propagate(False)
        
        # Добавляем тень справа от панели инструментов
        shadow = tk.Frame(main_frame, bg=self.colors['bg_dark'], width=2)
        shadow.pack(side=tk.LEFT, fill=tk.Y)
        
        # Средняя панель - рабочая область
        work_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        work_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Правая панель - докируемые панели
        self.dock_area = tk.Frame(main_frame, bg=self.colors['panel'], width=350)
        self.dock_area.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        self.dock_area.pack_propagate(False)
        
        # Настройка панелей
        self.setup_tool_panel()
        self.setup_work_area(work_frame)
        self.setup_dock_area()
        
        # Система докируемых окон
        self.docked_panels = {}
        self.floating_windows = {}
    
    def on_minimize(self, event):
        """Обработчик минимизации главного окна"""
        # Скрываем все плавающие панели когда главное окно минимизируется
        for window in self.floating_windows.values():
            try:
                window.withdraw()  # Прячем окно
            except:
                pass
    
    def on_restore(self, event):
        """Обработчик восстановления главного окна"""
        # Показываем все плавающие панели когда главное окно восстанавливается
        for window in self.floating_windows.values():
            try:
                window.deiconify()  # Показываем окно
            except:
                pass
    
    def setup_tool_panel(self):
        """Настройка компактной панели инструментов"""
        # Лого
        logo_label = tk.Label(self.tool_panel,
                             text="⚡",
                             bg=self.colors['panel'],
                             fg=self.colors['accent'],
                             font=('Segoe UI', 24))
        logo_label.pack(pady=(15, 20))
        
        # Кнопки инструментов с современным дизайном
        tools = [
            ("📁", "Файлы", self.show_files_panel),
            ("🎨", "Части", self.show_parts_panel), 
            ("🖼️", "Изображения", self.show_images_panel),
            ("👁️", "Превью", self.show_preview_panel),
            ("⚙️", "Настройки", self.show_settings_panel)
        ]
        
        for icon, tooltip, command in tools:
            # Создаем красивую кнопку без фрейма (прямо в панели)
            btn = tk.Label(self.tool_panel,
                          text=icon,
                          bg=self.colors['panel'],
                          fg=self.colors['accent'],
                          font=('Segoe UI', 18),
                          cursor='hand2',
                          width=3,
                          height=2,
                          anchor='center')
            btn.pack(pady=5, padx=5)
            
            # Hover эффекты
            def on_enter(e, b=btn):
                b.config(bg=self.colors['accent'], fg='white')
            
            def on_leave(e, b=btn):
                b.config(bg=self.colors['panel'], fg=self.colors['accent'])
            
            def on_click(e, cmd=command):
                cmd()
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn.bind('<Button-1>', on_click)
            
            # Добавляем tooltip
            self.create_tooltip(btn, tooltip)
    
    def create_tooltip(self, widget, text):
        """Создает всплывающую подсказку с современным дизайном"""
        tooltip_window = None
        
        def on_enter(event):
            nonlocal tooltip_window
            # Получаем актуальный текст подсказки
            tooltip_text = text() if callable(text) else text
            
            # Создаем окно подсказки
            tooltip_window = tk.Toplevel(self.root)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_attributes('-topmost', True)
            
            # Позиционируем около курсора
            x = event.x_root + 15
            y = event.y_root + 10
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            # Создаем красивую подсказку
            label = tk.Label(tooltip_window,
                           text=tooltip_text,
                           bg=self.colors['panel'],
                           fg=self.colors['accent'],
                           relief='solid',
                           borderwidth=2,
                           font=('Segoe UI', 9, 'bold'),
                           padx=10,
                           pady=5)
            label.pack()
        
        def on_leave(event):
            nonlocal tooltip_window
            if tooltip_window:
                try:
                    tooltip_window.destroy()
                except:
                    pass
                tooltip_window = None
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def setup_work_area(self, parent):
        """Настройка рабочей области"""
        # Заголовок рабочей области
        header = tk.Frame(parent, bg=self.colors['bg_dark'], height=40)
        header.pack(fill=tk.X, pady=(0, 10))
        
        work_title = tk.Label(header,
                             text="РАБОЧАЯ ОБЛАСТЬ",
                             bg=self.colors['bg_dark'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 10, 'bold'))
        work_title.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Контейнер для canvas с красивой рамкой
        canvas_container = tk.Frame(parent, 
                                   bg=self.colors['accent'],
                                   highlightthickness=2,
                                   highlightbackground=self.colors['accent'])
        canvas_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Canvas для отображения скина/плаща с градиентным фоном
        self.canvas = tk.Canvas(canvas_container,
                               bg=self.colors['bg_medium'],
                               width=600,
                               height=600,
                               highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
    
    def setup_dock_area(self):
        """Настройка области для докируемых панелей"""
        # Заголовок области с градиентом
        dock_title = tk.Label(self.dock_area,
                             text="ПАНЕЛИ",
                             bg=self.colors['panel'],
                             fg=self.colors['accent'],
                             font=('Segoe UI', 11, 'bold'))
        dock_title.pack(pady=(15, 15))
        
        # Контейнер для докированных панелей
        self.dock_container = tk.Frame(self.dock_area, bg=self.colors['panel'])
        self.dock_container.pack(fill=tk.BOTH, expand=True)
    
    def show_files_panel(self):
        """Показывает панель файлов"""
        self.show_panel("files", "Файлы", self.create_files_panel)
    
    def show_parts_panel(self):
        """Показывает панель частей"""
        self.show_panel("parts", "Части тела", self.create_parts_panel)
    
    def show_images_panel(self):
        """Показывает панель изображений"""
        self.show_panel("images", "Изображения", self.create_images_panel)
    
    def show_preview_panel(self):
        """Показывает панель превью"""
        self.show_panel("preview", "Превью", self.create_preview_panel)
    
    def show_settings_panel(self):
        """Показывает панель настроек"""
        self.show_panel("settings", "Настройки", self.create_settings_panel)
    
    def show_panel(self, panel_id, title, create_func):
        """Универсальный метод показа панели"""
        if panel_id in self.floating_windows:
            # Окно уже открыто - поднимаем его
            self.floating_windows[panel_id].lift()
            return
        
        if panel_id in self.docked_panels:
            # Панель уже докирована - скрываем/показываем
            panel = self.docked_panels[panel_id]
            if panel.winfo_viewable():
                panel.pack_forget()
            else:
                panel.pack(fill=tk.BOTH, expand=True, pady=2)
            return
        
        # Создаем новое плавающее окно
        self.create_floating_panel(panel_id, title, create_func)
    
    def create_floating_panel(self, panel_id, title, create_func):
        """Создает плавающее окно панели"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("350x400")
        window.resizable(True, True)
        
        # Делаем окно транзиентным (зависимым от главного окна)
        # Это заставит его минимизироваться вместе с главным окном
        window.transient(self.root)
        
        # Применяем темную тему к окну
        window.configure(bg=self.colors['panel'])
        
        # Заголовок с кнопкой закрепления
        header = tk.Frame(window, bg=self.colors['panel'])
        header.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(header, 
                              text=title, 
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['panel'],
                              fg=self.colors['accent'])
        title_label.pack(side=tk.LEFT)
        
        # Кнопка закрепления
        pin_btn = self.create_styled_button(header, "📌", 
                           command=lambda: self.dock_panel(panel_id, title, create_func, window),
                           primary=False)
        pin_btn.config(width=3, padx=5, pady=2)
        pin_btn.pack(side=tk.RIGHT)
        self.create_tooltip(pin_btn, "Закрепить панель")
        
        # Содержимое панели
        content_frame = tk.Frame(window, bg=self.colors['panel'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        create_func(content_frame)
        
        # Сохраняем ссылку на окно
        self.floating_windows[panel_id] = window
        
        # Обработчик закрытия окна
        def on_close():
            if panel_id in self.floating_windows:
                del self.floating_windows[panel_id]
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
    
    def dock_panel(self, panel_id, title, create_func, floating_window):
        """Закрепляет панель в док-области"""
        # Принудительно закрываем все tooltips
        self.close_all_tooltips()
        
        # Закрываем плавающее окно
        floating_window.destroy()
        if panel_id in self.floating_windows:
            del self.floating_windows[panel_id]
        
        # Создаем докированную панель с темной темой
        panel_frame = self.create_styled_labelframe(self.dock_container, title)
        panel_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Заголовок с кнопкой открепления
        header = tk.Frame(panel_frame, bg=self.colors['bg_light'])
        header.pack(fill=tk.X, padx=2, pady=2)
        
        # Кнопка открепления (используем другую иконку)
        unpin_btn = self.create_styled_button(header, "📍",
                             command=lambda: self.undock_panel(panel_id, title, create_func),
                             primary=False)
        unpin_btn.config(width=3, padx=5, pady=2)
        unpin_btn.pack(side=tk.RIGHT)
        self.create_tooltip(unpin_btn, "Открепить панель")
        
        # Содержимое панели
        content_frame = tk.Frame(panel_frame, bg=self.colors['bg_light'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        create_func(content_frame)
        
        # Сохраняем ссылку на панель
        self.docked_panels[panel_id] = panel_frame
    
    def undock_panel(self, panel_id, title, create_func):
        """Открепляет панель из док-области"""
        # Принудительно закрываем все tooltips
        self.close_all_tooltips()
        
        if panel_id in self.docked_panels:
            self.docked_panels[panel_id].destroy()
            del self.docked_panels[panel_id]
        
        # Создаем плавающее окно
        self.create_floating_panel(panel_id, title, create_func)
    
    def close_all_tooltips(self):
        """Закрывает все активные tooltips"""
        def close_tooltips_recursive(widget):
            if hasattr(widget, 'tooltip'):
                try:
                    widget.tooltip.destroy()
                    del widget.tooltip
                except:
                    pass
            
            # Рекурсивно проверяем дочерние виджеты
            try:
                for child in widget.winfo_children():
                    close_tooltips_recursive(child)
            except:
                pass
        
        # Закрываем tooltips во всех окнах
        close_tooltips_recursive(self.root)
        for window in self.floating_windows.values():
            close_tooltips_recursive(window)
    
    def create_files_panel(self, parent):
        """Создает содержимое панели файлов"""
        parent.configure(bg=self.colors['panel'])
        
        # Управление скинами
        skin_frame = self.create_styled_labelframe(parent, "📁 СКИНЫ")
        skin_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        self.create_styled_button(skin_frame, "Загрузить скин", self.load_skin, primary=True).pack(fill=tk.X, pady=3, padx=5)
        self.create_styled_button(skin_frame, "Сохранить скин", self.save_skin).pack(fill=tk.X, pady=3, padx=5)
        self.create_styled_button(skin_frame, "Новый скин", self.create_default_skin).pack(fill=tk.X, pady=3, padx=5)
        
        # Переключатель плаща
        cape_frame = self.create_styled_labelframe(parent, "🎪 ПЛАЩИ")
        cape_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        self.cape_var = tk.BooleanVar()
        cape_check = tk.Checkbutton(cape_frame,
                                    text="Режим плаща",
                                    variable=self.cape_var,
                                    command=self.toggle_cape_mode,
                                    bg=self.colors['bg_light'],
                                    fg=self.colors['text'],
                                    selectcolor=self.colors['accent'],
                                    activebackground=self.colors['bg_light'],
                                    activeforeground=self.colors['accent'],
                                    font=('Segoe UI', 9))
        cape_check.pack(fill=tk.X, pady=5, padx=5)
        
        self.create_styled_button(cape_frame, "Загрузить плащ", self.load_cape, primary=True).pack(fill=tk.X, pady=3, padx=5)
        self.create_styled_button(cape_frame, "Сохранить плащ", self.save_cape).pack(fill=tk.X, pady=3, padx=5)
        self.create_styled_button(cape_frame, "Новый плащ", self.create_default_cape).pack(fill=tk.X, pady=3, padx=5)
        
        # Размер
        size_frame = self.create_styled_labelframe(parent, "📏 РАЗМЕР")
        size_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        self.size_var = tk.StringVar(value="64x64")
        
        for value, text in [("64x64", "64x64 (Стандартный)"), ("1024x1024", "1024x1024 (HD)")]:
            rb = tk.Radiobutton(size_frame,
                               text=text,
                               variable=self.size_var,
                               value=value,
                               command=self.change_skin_size,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['accent'],
                               activebackground=self.colors['bg_light'],
                               activeforeground=self.colors['accent'],
                               font=('Segoe UI', 9))
            rb.pack(anchor=tk.W, pady=2, padx=5)
    
    def create_styled_labelframe(self, parent, text):
        """Создает стильный LabelFrame"""
        frame = tk.LabelFrame(parent,
                             text=text,
                             bg=self.colors['bg_light'],
                             fg=self.colors['accent'],
                             font=('Segoe UI', 9, 'bold'),
                             relief='flat',
                             borderwidth=2,
                             highlightthickness=1,
                             highlightbackground=self.colors['accent'])
        return frame
    
    def create_styled_button(self, parent, text, command, primary=False):
        """Создает стильную кнопку с приятными цветами"""
        bg_color = self.colors['button_primary'] if primary else self.colors['button_secondary']
        fg_color = self.colors['text'] if primary else self.colors['text']
        hover_bg = self.colors['accent_hover'] if primary else self.colors['panel_hover']
        
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=bg_color,
                       fg=fg_color,
                       font=('Segoe UI', 9, 'bold' if primary else 'normal'),
                       relief='flat',
                       cursor='hand2',
                       borderwidth=0,
                       padx=15,
                       pady=8,
                       activebackground=hover_bg,
                       activeforeground=self.colors['text'])
        
        # Hover эффект
        def on_enter(e):
            btn.config(bg=hover_bg)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_parts_panel(self, parent):
        """Создает содержимое панели частей"""
        parent.configure(bg=self.colors['panel'])
        
        # Кнопки быстрого выбора
        quick_frame = self.create_styled_labelframe(parent, "Быстрый выбор")
        quick_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.create_styled_button(quick_frame, "Основной слой", 
                  self.select_main_layer, primary=True).pack(fill=tk.X, pady=2, padx=5)
        self.create_styled_button(quick_frame, "Второй слой", 
                  self.select_overlay_layer).pack(fill=tk.X, pady=2, padx=5)
        self.create_styled_button(quick_frame, "Очистить выбор", 
                  self.clear_selection).pack(fill=tk.X, pady=2, padx=5)
        
        # Дерево частей
        tree_frame = self.create_styled_labelframe(parent, "Части тела")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=10)
        
        # Создаем Treeview
        tree_container = tk.Frame(tree_frame, bg=self.colors['bg_light'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.body_tree = ttk.Treeview(tree_container, height=12, selectmode='extended')
        self.body_tree.heading('#0', text='Части скина/плаща')
        
        # Настраиваем стили
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        # События
        self.body_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.body_tree.bind('<Control-Button-1>', self.on_ctrl_click)
        self.body_tree.bind('<Button-1>', self.on_single_click)
        
        # Скроллбар
        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.body_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.body_tree.configure(yscrollcommand=tree_scroll.set)
        self.body_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Информация о выборе
        self.selection_info = tk.Label(tree_frame, 
                                      text="Выбрано: 0 частей", 
                                      font=('Segoe UI', 8),
                                      bg=self.colors['bg_light'],
                                      fg=self.colors['accent'])
        self.selection_info.pack(pady=5)
    
    def create_images_panel(self, parent):
        """Создает содержимое панели изображений"""
        parent.configure(bg=self.colors['panel'])
        
        # Применение изображений
        apply_frame = self.create_styled_labelframe(parent, "Применение")
        apply_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.create_styled_button(apply_frame, "Добавить на выбранные части", 
                  self.add_image_to_selected_regions, primary=True).pack(fill=tk.X, pady=2, padx=5)
        
        # Режим применения
        mode_frame = self.create_styled_labelframe(parent, "Режим применения")
        mode_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.multi_mode = tk.StringVar(value="individual")
        
        rb1 = tk.Radiobutton(mode_frame, 
                            text="На каждую часть отдельно", 
                            variable=self.multi_mode, 
                            value="individual",
                            bg=self.colors['bg_light'],
                            fg=self.colors['text'],
                            selectcolor=self.colors['accent'],
                            activebackground=self.colors['bg_light'],
                            activeforeground=self.colors['accent'],
                            font=('Segoe UI', 9))
        rb1.pack(anchor=tk.W, padx=5, pady=2)
        
        rb2 = tk.Radiobutton(mode_frame, 
                            text="Растянуть на все выбранные", 
                            variable=self.multi_mode, 
                            value="stretch",
                            bg=self.colors['bg_light'],
                            fg=self.colors['text'],
                            selectcolor=self.colors['accent'],
                            activebackground=self.colors['bg_light'],
                            activeforeground=self.colors['accent'],
                            font=('Segoe UI', 9))
        rb2.pack(anchor=tk.W, padx=5, pady=2)
        
        # Пул изображений
        pool_frame = self.create_styled_labelframe(parent, "Пул изображений")
        pool_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.create_styled_button(pool_frame, "Загрузить пул изображений", 
                  self.load_image_pool).pack(fill=tk.X, pady=2, padx=5)
        self.create_styled_button(pool_frame, "Рандомизировать пул по частям", 
                  self.randomize_pool_to_regions).pack(fill=tk.X, pady=2, padx=5)
        
        # 3D обертка
        wrap_frame = self.create_styled_labelframe(parent, "3D обертка")
        wrap_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.create_styled_button(wrap_frame, "Полная 3D обертка (6 сторон)", 
                  self.stretch_to_four_sides, primary=True).pack(fill=tk.X, pady=2, padx=5)
        self.create_styled_button(wrap_frame, "Очистить выбранные части", 
                  self.clear_selected_regions).pack(fill=tk.X, pady=2, padx=5)
        
        # Переменные для пула изображений
        self.image_pool = []
    
    def create_preview_panel(self, parent):
        """Создает содержимое панели превью"""
        parent.configure(bg=self.colors['panel'])
        
        preview_frame = self.create_styled_labelframe(parent, "Превью скина")
        preview_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        self.create_styled_button(preview_frame, "3D Превью скина", 
                  self.show_3d_preview, primary=True).pack(fill=tk.X, pady=2, padx=5)
        self.create_styled_button(preview_frame, "Показать развертку", 
                  self.show_skin_layout).pack(fill=tk.X, pady=2, padx=5)
    
    def create_settings_panel(self, parent):
        """Создает содержимое панели настроек"""
        parent.configure(bg=self.colors['panel'])
        
        settings_frame = self.create_styled_labelframe(parent, "Настройки отображения")
        settings_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        # Здесь можно добавить различные настройки
        info_label = tk.Label(settings_frame, 
                             text="Настройки будут добавлены позже",
                             bg=self.colors['bg_light'],
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 9))
        info_label.pack(pady=10, padx=5)
        
    def create_default_skin(self):
        """Создает пустой скин"""
        size = 64 if self.size_var.get() == "64x64" else 1024
        self.skin_size = size
        self.current_skin = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.update_display()
    
    def create_default_cape(self):
        """Создает пустой плащ"""
        # Размер плаща зависит от размера скина
        cape_width = 64 if self.size_var.get() == "64x64" else 1024
        cape_height = 32 if self.size_var.get() == "64x64" else 512
        self.cape_size = cape_width
        self.current_cape = Image.new("RGBA", (cape_width, cape_height), (0, 0, 0, 0))
        self.cape_enabled = True
        self.cape_var.set(True)
        self.update_display()
    
    def toggle_cape_mode(self):
        """Переключает режим плаща"""
        self.cape_enabled = self.cape_var.get()
        if self.cape_enabled and not self.current_cape:
            self.create_default_cape()
        self.setup_skin_tree()
        self.update_display()
    
    def setup_skin_tree(self):
        """Настраивает дерево в зависимости от режима (скин/плащ)"""
        if not self.body_tree:
            return  # Дерево еще не создано
            
        # Очищаем дерево
        for item in self.body_tree.get_children():
            self.body_tree.delete(item)
        
        if self.cape_enabled:
            # Режим плаща
            self.body_tree.heading('#0', text='Части плаща')
            self.all_group = self.body_tree.insert('', 'end', text='ВСЕ ЧАСТИ ПЛАЩА', open=True, values=('ALL_CAPE',))
            
            cape_parts = [
                ("Задняя часть", "cape_back"),
                ("Передняя часть", "cape_front"), 
                ("Правая сторона", "cape_right"),
                ("Левая сторона", "cape_left"),
                ("Верх", "cape_top"),
                ("Низ", "cape_bottom")
            ]
            
            for text, value in cape_parts:
                self.body_tree.insert('', 'end', text=text, values=(value,))
        else:
            # Режим скина
            self.body_tree.heading('#0', text='Части скина')
            self.all_group = self.body_tree.insert('', 'end', text='ВСЕ ЧАСТИ СКИНА', open=True, values=('ALL',))
            head_group = self.body_tree.insert('', 'end', text='Голова (основной слой)', open=True, values=('head_main',))
            head_overlay_group = self.body_tree.insert('', 'end', text='Голова (второй слой)', open=False, values=('head_overlay',))
            body_group = self.body_tree.insert('', 'end', text='Тело (основной слой)', open=True, values=('body_main',))
            body_overlay_group = self.body_tree.insert('', 'end', text='Тело (второй слой)', open=False, values=('body_overlay',))
            arm_right_group = self.body_tree.insert('', 'end', text='Правая рука (основной слой)', open=False, values=('arm_right_main',))
            arm_right_overlay_group = self.body_tree.insert('', 'end', text='Правая рука (второй слой)', open=False, values=('arm_right_overlay',))
            arm_left_group = self.body_tree.insert('', 'end', text='Левая рука (основной слой)', open=False, values=('arm_left_main',))
            arm_left_overlay_group = self.body_tree.insert('', 'end', text='Левая рука (второй слой)', open=False, values=('arm_left_overlay',))
            leg_right_group = self.body_tree.insert('', 'end', text='Правая нога (основной слой)', open=False, values=('leg_right_main',))
            leg_right_overlay_group = self.body_tree.insert('', 'end', text='Правая нога (второй слой)', open=False, values=('leg_right_overlay',))
            leg_left_group = self.body_tree.insert('', 'end', text='Левая нога (основной слой)', open=False, values=('leg_left_main',))
            leg_left_overlay_group = self.body_tree.insert('', 'end', text='Левая нога (второй слой)', open=False, values=('leg_left_overlay',))
            
            # Добавляем элементы в группы
            head_parts = [
                ("Лицо", "head_front"), ("Затылок", "head_back"), ("Правая сторона", "head_right"),
                ("Левая сторона", "head_left"), ("Верх", "head_top"), ("Низ", "head_bottom")
            ]
            head_overlay_parts = [
                ("Шляпа - Лицо", "head_overlay_front"), ("Шляпа - Затылок", "head_overlay_back"),
                ("Шляпа - Правая сторона", "head_overlay_right"), ("Шляпа - Левая сторона", "head_overlay_left"),
                ("Шляпа - Верх", "head_overlay_top"), ("Шляпа - Низ", "head_overlay_bottom")
            ]
            body_parts = [
                ("Перед", "body_front"), ("Зад", "body_back"), ("Правая сторона", "body_right"),
                ("Левая сторона", "body_left"), ("Верх", "body_top"), ("Низ", "body_bottom")
            ]
            body_overlay_parts = [
                ("Куртка - Перед", "body_overlay_front"), ("Куртка - Зад", "body_overlay_back"),
                ("Куртка - Правая сторона", "body_overlay_right"), ("Куртка - Левая сторона", "body_overlay_left"),
                ("Куртка - Верх", "body_overlay_top"), ("Куртка - Низ", "body_overlay_bottom")
            ]
            
            arm_parts = [
                ("Перед", "front"), ("Зад", "back"), ("Внешняя сторона", "right"),
                ("Внутренняя сторона", "left"), ("Верх", "top"), ("Низ", "bottom")
            ]
            
            leg_parts = [
                ("Перед", "front"), ("Зад", "back"), ("Внешняя сторона", "right"),
                ("Внутренняя сторона", "left"), ("Верх", "top"), ("Низ", "bottom")
            ]
            
            # Заполняем дерево
            for text, value in head_parts:
                self.body_tree.insert(head_group, 'end', text=text, values=(value,))
            for text, value in head_overlay_parts:
                self.body_tree.insert(head_overlay_group, 'end', text=text, values=(value,))
            for text, value in body_parts:
                self.body_tree.insert(body_group, 'end', text=text, values=(value,))
            for text, value in body_overlay_parts:
                self.body_tree.insert(body_overlay_group, 'end', text=text, values=(value,))
                
            # Руки и ноги
            for text, suffix in arm_parts:
                self.body_tree.insert(arm_right_group, 'end', text=text, values=(f"arm_right_{suffix}",))
                self.body_tree.insert(arm_right_overlay_group, 'end', text=f"Рукав - {text}", values=(f"arm_right_overlay_{suffix}",))
                self.body_tree.insert(arm_left_group, 'end', text=text, values=(f"arm_left_{suffix}",))
                self.body_tree.insert(arm_left_overlay_group, 'end', text=f"Рукав - {text}", values=(f"arm_left_overlay_{suffix}",))
                
            for text, suffix in leg_parts:
                self.body_tree.insert(leg_right_group, 'end', text=text, values=(f"leg_right_{suffix}",))
                self.body_tree.insert(leg_right_overlay_group, 'end', text=f"Штанина - {text}", values=(f"leg_right_overlay_{suffix}",))
                self.body_tree.insert(leg_left_group, 'end', text=text, values=(f"leg_left_{suffix}",))
                self.body_tree.insert(leg_left_overlay_group, 'end', text=f"Штанина - {text}", values=(f"leg_left_overlay_{suffix}",))
        
    def load_cape(self):
        """Загружает плащ из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл плаща",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                # Поддерживаем стандартные (64x32) и HD (1024x512) плащи
                if img.size == (64, 32) or img.size == (1024, 512):
                    self.current_cape = img.convert("RGBA")
                    self.cape_size = img.size[0]
                    self.cape_enabled = True
                    self.cape_var.set(True)
                    self.setup_skin_tree()
                    self.update_display()
                    messagebox.showinfo("Успех", f"Плащ {img.size[0]}x{img.size[1]} загружен успешно!")
                else:
                    messagebox.showerror("Ошибка", "Плащ должен быть размером 64x32 или 1024x512")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить плащ: {str(e)}")
    
    def save_cape(self):
        """Сохраняет плащ в файл"""
        if not self.current_cape:
            messagebox.showwarning("Предупреждение", "Нет плаща для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить плащ",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_cape.save(file_path, "PNG")
                messagebox.showinfo("Успех", "Плащ сохранен успешно!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить плащ: {str(e)}")
    
    def change_skin_size(self):
        """Изменяет размер скина"""
        if self.current_skin:
            new_size = 64 if self.size_var.get() == "64x64" else 1024
            if new_size != self.skin_size:
                # Масштабируем существующий скин
                self.current_skin = self.current_skin.resize((new_size, new_size), Image.NEAREST)
                self.skin_size = new_size
                self.update_display()
        
        # Обновляем размер плаща если он есть
        if self.current_cape:
            new_cape_width = 64 if self.size_var.get() == "64x64" else 1024
            new_cape_height = 32 if self.size_var.get() == "64x64" else 512
            if new_cape_width != self.cape_size:
                self.current_cape = self.current_cape.resize((new_cape_width, new_cape_height), Image.NEAREST)
                self.cape_size = new_cape_width
                self.update_display()
    
    def get_scaled_region(self, region_name):
        """Получает координаты региона с учетом масштаба"""
        if region_name in self.cape_regions:
            # Масштабируем координаты плаща
            base_coords = self.cape_regions[region_name]
            scale = self.cape_size / 64  # Базовые координаты для 64x32
            return tuple(int(coord * scale) for coord in base_coords)
        elif region_name in self.skin_regions:
            base_coords = self.skin_regions[region_name]
            scale = self.skin_size / 64
            return tuple(int(coord * scale) for coord in base_coords)
        else:
            return (0, 0, 0, 0)
    
    def load_skin(self):
        """Загружает скин из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл скина",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                if img.size[0] == img.size[1] and img.size[0] in [64, 1024]:
                    self.current_skin = img.convert("RGBA")
                    self.skin_size = img.size[0]
                    self.size_var.set(f"{self.skin_size}x{self.skin_size}")
                    self.update_display()
                    messagebox.showinfo("Успех", "Скин загружен успешно!")
                else:
                    messagebox.showerror("Ошибка", "Скин должен быть квадратным 64x64 или 1024x1024")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить скин: {str(e)}")
    
    def save_skin(self):
        """Сохраняет скин в файл"""
        if not self.current_skin:
            messagebox.showwarning("Предупреждение", "Нет скина для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить скин",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_skin.save(file_path, "PNG")
                messagebox.showinfo("Успех", "Скин сохранен успешно!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить скин: {str(e)}")
    
    def on_tree_select(self, event):
        """Обработчик выбора в дереве - автоматически выбирает дочерние элементы"""
        selected_items = self.body_tree.selection()
        
        for item in selected_items:
            values = self.body_tree.item(item, 'values')
            if values and len(values) > 0:
                group_type = values[0]
                
                # Если выбрана группа, выбираем все её дочерние элементы
                if group_type in ['ALL', 'ALL_CAPE', 'head_main', 'head_overlay', 'body_main', 'body_overlay', 
                                'arm_right_main', 'arm_right_overlay', 'arm_left_main', 'arm_left_overlay',
                                'leg_right_main', 'leg_right_overlay', 'leg_left_main', 'leg_left_overlay']:
                    
                    if group_type == 'ALL':
                        # Выбираем все элементы скина
                        self.select_all_regions()
                    elif group_type == 'ALL_CAPE':
                        # Выбираем все элементы плаща
                        self.select_all_cape_regions()
                    else:
                        # Выбираем дочерние элементы группы
                        self.select_group_children(item)
        
        # Обновляем информацию о выборе
        self.update_selection_info()
    
    def select_all_cape_regions(self):
        """Выбирает все регионы плаща"""
        # Очищаем текущий выбор
        for item in self.body_tree.selection():
            self.body_tree.selection_remove(item)
        
        # Выбираем все элементы плаща
        def select_all_cape_items(parent=""):
            for child in self.body_tree.get_children(parent):
                values = self.body_tree.item(child, 'values')
                if values and values[0] not in ['ALL_CAPE']:
                    self.body_tree.selection_add(child)
                select_all_cape_items(child)
        
        select_all_cape_items()
    
    def select_main_layer(self):
        """Выбирает все части основного слоя"""
        if self.cape_enabled:
            # Для плащей выбираем все части
            self.select_all_cape_regions()
            return
            
        # Очищаем текущий выбор
        for item in self.body_tree.selection():
            self.body_tree.selection_remove(item)
        
        # Выбираем только основной слой
        main_layer_groups = ['head_main', 'body_main', 'arm_right_main', 'arm_left_main', 
                           'leg_right_main', 'leg_left_main']
        
        def select_main_items(parent=""):
            for child in self.body_tree.get_children(parent):
                values = self.body_tree.item(child, 'values')
                if values and len(values) > 0:
                    value = values[0]
                    # Выбираем элементы основного слоя (без overlay)
                    if value in main_layer_groups:
                        # Выбираем все дочерние элементы группы
                        for subchild in self.body_tree.get_children(child):
                            self.body_tree.selection_add(subchild)
                    elif 'overlay' not in value and value not in ['ALL'] + main_layer_groups:
                        # Выбираем отдельные элементы основного слоя
                        if not any(overlay in value for overlay in ['overlay']):
                            self.body_tree.selection_add(child)
                select_main_items(child)
        
        select_main_items()
        self.update_selection_info()
    
    def select_overlay_layer(self):
        """Выбирает все части второго слоя (overlay)"""
        if self.cape_enabled:
            # Для плащей нет второго слоя
            messagebox.showinfo("Информация", "У плащей нет второго слоя")
            return
            
        # Очищаем текущий выбор
        for item in self.body_tree.selection():
            self.body_tree.selection_remove(item)
        
        # Выбираем только второй слой
        overlay_groups = ['head_overlay', 'body_overlay', 'arm_right_overlay', 'arm_left_overlay', 
                         'leg_right_overlay', 'leg_left_overlay']
        
        def select_overlay_items(parent=""):
            for child in self.body_tree.get_children(parent):
                values = self.body_tree.item(child, 'values')
                if values and len(values) > 0:
                    value = values[0]
                    # Выбираем элементы второго слоя
                    if value in overlay_groups:
                        # Выбираем все дочерние элементы группы
                        for subchild in self.body_tree.get_children(child):
                            self.body_tree.selection_add(subchild)
                    elif 'overlay' in value and value not in overlay_groups:
                        # Выбираем отдельные элементы второго слоя
                        self.body_tree.selection_add(child)
                select_overlay_items(child)
        
        select_overlay_items()
        self.update_selection_info()
    
    def clear_selection(self):
        """Очищает выбор"""
        for item in self.body_tree.selection():
            self.body_tree.selection_remove(item)
        self.update_selection_info()
    
    def update_selection_info(self):
        """Обновляет информацию о выборе"""
        if not self.selection_info:
            return
        selected_count = len(self.get_selected_regions())
        item_type = "плаща" if self.cape_enabled else "скина"
        self.selection_info.config(text=f"Выбрано: {selected_count} частей {item_type}")
    
    def on_ctrl_click(self, event):
        """Обработчик Ctrl+клик для множественного выбора групп"""
        item = self.body_tree.identify('item', event.x, event.y)
        if item:
            values = self.body_tree.item(item, 'values')
            if values and len(values) > 0:
                group_type = values[0]
                
                # Если это группа, выбираем/снимаем выбор с её дочерних элементов
                if group_type in ['ALL', 'ALL_CAPE', 'head_main', 'head_overlay', 'body_main', 'body_overlay', 
                                'arm_right_main', 'arm_right_overlay', 'arm_left_main', 'arm_left_overlay',
                                'leg_right_main', 'leg_right_overlay', 'leg_left_main', 'leg_left_overlay']:
                    
                    # Проверяем, выбраны ли уже дочерние элементы
                    children = list(self.body_tree.get_children(item))
                    selected_children = [child for child in children if child in self.body_tree.selection()]
                    
                    if len(selected_children) == len(children):
                        # Все дочерние выбраны - снимаем выбор
                        for child in children:
                            self.body_tree.selection_remove(child)
                    else:
                        # Не все выбраны - выбираем все
                        for child in children:
                            self.body_tree.selection_add(child)
                    
                    self.update_selection_info()
                    return "break"  # Предотвращаем стандартное поведение
    
    def on_single_click(self, event):
        """Обработчик обычного клика"""
        # Обновляем информацию о выборе после клика
        self.body_tree.after(10, self.update_selection_info)
    
    def select_all_regions(self):
        """Выбирает все регионы скина"""
        # Очищаем текущий выбор
        for item in self.body_tree.selection():
            self.body_tree.selection_remove(item)
        
        # Выбираем все элементы с values (не группы)
        def select_all_items(parent=""):
            for child in self.body_tree.get_children(parent):
                values = self.body_tree.item(child, 'values')
                if values and values[0] not in ['ALL', 'head_main', 'head_overlay', 'body_main', 'body_overlay', 
                                              'arm_right_main', 'arm_right_overlay', 'arm_left_main', 'arm_left_overlay',
                                              'leg_right_main', 'leg_right_overlay', 'leg_left_main', 'leg_left_overlay']:
                    self.body_tree.selection_add(child)
                select_all_items(child)
        
        select_all_items()
        self.update_selection_info()
    
    def select_group_children(self, group_item):
        """Выбирает все дочерние элементы группы"""
        # Убираем выбор с самой группы
        self.body_tree.selection_remove(group_item)
        
        # Выбираем все дочерние элементы
        for child in self.body_tree.get_children(group_item):
            values = self.body_tree.item(child, 'values')
            if values and values[0] not in ['ALL', 'ALL_CAPE', 'head_main', 'head_overlay', 'body_main', 'body_overlay', 
                                          'arm_right_main', 'arm_right_overlay', 'arm_left_main', 'arm_left_overlay',
                                          'leg_right_main', 'leg_right_overlay', 'leg_left_main', 'leg_left_overlay']:
                self.body_tree.selection_add(child)
        self.update_selection_info()
    
    def get_selected_regions(self):
        """Получает список выбранных регионов"""
        selected_items = self.body_tree.selection()
        regions = []
        
        for item in selected_items:
            values = self.body_tree.item(item, 'values')
            if values and len(values) > 0:
                region_name = values[0]
                # Пропускаем группы
                if region_name not in ['ALL', 'ALL_CAPE', 'head_main', 'head_overlay', 'body_main', 'body_overlay', 
                                     'arm_right_main', 'arm_right_overlay', 'arm_left_main', 'arm_left_overlay',
                                     'leg_right_main', 'leg_right_overlay', 'leg_left_main', 'leg_left_overlay']:
                    regions.append(region_name)
        
        return regions
    
    def load_image_pool(self):
        """Загружает пул изображений"""
        file_paths = filedialog.askopenfilenames(
            title="Выберите изображения для пула",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if file_paths:
            self.image_pool = []
            for file_path in file_paths:
                try:
                    img = Image.open(file_path).convert("RGBA")
                    self.image_pool.append(img)
                except Exception as e:
                    print(f"Ошибка загрузки {file_path}: {e}")
            
            messagebox.showinfo("Успех", f"Загружено {len(self.image_pool)} изображений в пул")
    
    def randomize_pool_to_regions(self):
        """Рандомно распределяет изображения из пула по выбранным регионам"""
        if not self.current_skin:
            messagebox.showwarning("Предупреждение", "Сначала создайте или загрузите скин")
            return
            
        if not self.image_pool:
            messagebox.showwarning("Предупреждение", "Сначала загрузите пул изображений")
            return
            
        selected_regions = self.get_selected_regions()
        if not selected_regions:
            messagebox.showwarning("Предупреждение", "Выберите части скина")
            return
        
        import random
        
        for region_name in selected_regions:
            if region_name in self.skin_regions:
                # Выбираем случайное изображение из пула
                random_img = random.choice(self.image_pool)
                
                x1, y1, x2, y2 = self.get_scaled_region(region_name)
                region_width = x2 - x1
                region_height = y2 - y1
                
                # Масштабируем изображение под размер региона
                resized_img = random_img.resize((region_width, region_height), Image.LANCZOS)
                self.current_skin.paste(resized_img, (x1, y1), resized_img)
        
        self.update_display()
        messagebox.showinfo("Успех", f"Рандомизировано {len(selected_regions)} частей из пула {len(self.image_pool)} изображений")
    
    def stretch_to_four_sides(self):
        """Растягивает изображение на все 6 сторон скина как полная 3D обертка"""
        if not self.current_skin:
            messagebox.showwarning("Предупреждение", "Сначала создайте или загрузите скин")
            return
            
        file_path = filedialog.askopenfilename(
            title="Выберите изображение для полной 3D обертки",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path).convert("RGBA")
                
                # Определяем логические группы для полной 3D обертки (все 6 сторон)
                front_parts = [
                    "head_front", "body_front", 
                    "arm_right_front", "arm_left_front",
                    "leg_right_front", "leg_left_front"
                ]
                
                back_parts = [
                    "head_back", "body_back",
                    "arm_right_back", "arm_left_back", 
                    "leg_right_back", "leg_left_back"
                ]
                
                right_parts = [
                    "head_right", "body_right",
                    "arm_right_right", "arm_left_right",
                    "leg_right_right", "leg_left_right"
                ]
                
                left_parts = [
                    "head_left", "body_left",
                    "arm_right_left", "arm_left_left",
                    "leg_right_left", "leg_left_left"
                ]
                
                top_parts = [
                    "head_top", "body_top",
                    "arm_right_top", "arm_left_top",
                    "leg_right_top", "leg_left_top"
                ]
                
                bottom_parts = [
                    "head_bottom", "body_bottom",
                    "arm_right_bottom", "arm_left_bottom",
                    "leg_right_bottom", "leg_left_bottom"
                ]
                
                # Применяем одно и то же изображение ко всем 6 сторонам
                self.apply_3d_wrap_to_side(img, front_parts, "front")
                self.apply_3d_wrap_to_side(img, back_parts, "back") 
                self.apply_3d_wrap_to_side(img, right_parts, "right")
                self.apply_3d_wrap_to_side(img, left_parts, "left")
                self.apply_3d_wrap_to_side(img, top_parts, "top")
                self.apply_3d_wrap_to_side(img, bottom_parts, "bottom")
                
                self.update_display()
                messagebox.showinfo("Успех", "Изображение применено как полная 3D обертка (6 сторон)")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить изображение: {str(e)}")
    
    def apply_3d_wrap_to_side(self, img, parts_list, side_name):
        """Применяет изображение к одной логической стороне как 3D обертка"""
        # Создаем виртуальную сетку для этой стороны
        # Размеры масштабируются пропорционально размеру скина для сохранения качества
        scale_factor = self.skin_size / 64  # Для 64x64 = 1, для 1024x1024 = 16
        
        virtual_width = int(20 * scale_factor)   # Масштабируем под размер скина
        virtual_height = int(36 * scale_factor)  # Сохраняем пропорции
        
        # Масштабируем исходное изображение под виртуальную сетку
        # Для HD скинов используем большую сетку = лучшее качество
        scaled_img = img.resize((virtual_width, virtual_height), Image.LANCZOS)
        
        # Для задней стороны отзеркаливаем изображение по горизонтали
        if side_name == "back":
            scaled_img = scaled_img.transpose(Image.FLIP_LEFT_RIGHT)
        
        # Определяем позиции частей в виртуальной сетке с учетом всех сторон
        # Координаты масштабируются пропорционально размеру скина
        if side_name in ["front", "back"]:
            # Для передней и задней стороны - стандартная раскладка
            # Для задней стороны руки уже отзеркалены вместе с изображением
            part_positions = {
                "head": (int(6*scale_factor), int(0*scale_factor), int(14*scale_factor), int(9*scale_factor)),
                "body": (int(6*scale_factor), int(9*scale_factor), int(14*scale_factor), int(21*scale_factor)),
                "arm_right": (int(2*scale_factor), int(9*scale_factor), int(6*scale_factor), int(21*scale_factor)),
                "arm_left": (int(14*scale_factor), int(9*scale_factor), int(18*scale_factor), int(21*scale_factor)),
                "leg_right": (int(6*scale_factor), int(21*scale_factor), int(10*scale_factor), int(36*scale_factor)),
                "leg_left": (int(10*scale_factor), int(21*scale_factor), int(14*scale_factor), int(36*scale_factor))
            }
        elif side_name in ["right", "left"]:
            # Для боковых сторон - более узкая раскладка
            part_positions = {
                "head": (int(8*scale_factor), int(0*scale_factor), int(12*scale_factor), int(9*scale_factor)),
                "body": (int(8*scale_factor), int(9*scale_factor), int(12*scale_factor), int(21*scale_factor)),
                "arm_right": (int(4*scale_factor), int(9*scale_factor), int(8*scale_factor), int(21*scale_factor)),
                "arm_left": (int(12*scale_factor), int(9*scale_factor), int(16*scale_factor), int(21*scale_factor)),
                "leg_right": (int(8*scale_factor), int(21*scale_factor), int(10*scale_factor), int(36*scale_factor)),
                "leg_left": (int(10*scale_factor), int(21*scale_factor), int(12*scale_factor), int(36*scale_factor))
            }
        elif side_name in ["top", "bottom"]:
            # Для верхней и нижней сторон - горизонтальная раскладка
            part_positions = {
                "head": (int(6*scale_factor), int(6*scale_factor), int(14*scale_factor), int(14*scale_factor)),
                "body": (int(6*scale_factor), int(14*scale_factor), int(14*scale_factor), int(22*scale_factor)),
                "arm_right": (int(2*scale_factor), int(14*scale_factor), int(6*scale_factor), int(18*scale_factor)),
                "arm_left": (int(14*scale_factor), int(14*scale_factor), int(18*scale_factor), int(18*scale_factor)),
                "leg_right": (int(6*scale_factor), int(22*scale_factor), int(10*scale_factor), int(26*scale_factor)),
                "leg_left": (int(10*scale_factor), int(22*scale_factor), int(14*scale_factor), int(26*scale_factor))
            }
        else:
            # Fallback - стандартная раскладка
            part_positions = {
                "head": (int(6*scale_factor), int(0*scale_factor), int(14*scale_factor), int(9*scale_factor)),
                "body": (int(6*scale_factor), int(9*scale_factor), int(14*scale_factor), int(21*scale_factor)),
                "arm_right": (int(2*scale_factor), int(9*scale_factor), int(6*scale_factor), int(21*scale_factor)),
                "arm_left": (int(14*scale_factor), int(9*scale_factor), int(18*scale_factor), int(21*scale_factor)),
                "leg_right": (int(6*scale_factor), int(21*scale_factor), int(10*scale_factor), int(36*scale_factor)),
                "leg_left": (int(10*scale_factor), int(21*scale_factor), int(14*scale_factor), int(36*scale_factor))
            }
        
        # Применяем части изображения к соответствующим регионам скина
        for part_name in parts_list:
            if part_name not in self.skin_regions:
                continue
                
            # Определяем тип части (голова, тело, рука, нога)
            part_type = None
            if "head_" in part_name:
                part_type = "head"
            elif "body_" in part_name:
                part_type = "body"
            elif "arm_right_" in part_name:
                part_type = "arm_right"
            elif "arm_left_" in part_name:
                part_type = "arm_left"
            elif "leg_right_" in part_name:
                part_type = "leg_right"
            elif "leg_left_" in part_name:
                part_type = "leg_left"
            
            if part_type and part_type in part_positions:
                # Получаем область из виртуальной сетки
                vx1, vy1, vx2, vy2 = part_positions[part_type]
                
                # Проверяем границы
                if vx2 <= virtual_width and vy2 <= virtual_height:
                    part_img = scaled_img.crop((vx1, vy1, vx2, vy2))
                    
                    # Получаем координаты на скине
                    x1, y1, x2, y2 = self.get_scaled_region(part_name)
                    
                    # Масштабируем под размер региона на скине
                    region_width = x2 - x1
                    region_height = y2 - y1
                    
                    if region_width > 0 and region_height > 0:
                        final_img = part_img.resize((region_width, region_height), Image.LANCZOS)
                        
                        # Применяем к скину
                        self.current_skin.paste(final_img, (x1, y1), final_img)
    
    def add_image_to_selected_regions(self):
        """Добавляет изображение на выбранные части скина или плаща"""
        current_image = self.current_cape if self.cape_enabled else self.current_skin
        
        if not current_image:
            item_type = "плащ" if self.cape_enabled else "скин"
            messagebox.showwarning("Предупреждение", f"Сначала создайте или загрузите {item_type}")
            return
            
        selected_regions = self.get_selected_regions()
        if not selected_regions:
            item_type = "плаща" if self.cape_enabled else "скина"
            messagebox.showwarning("Предупреждение", f"Выберите части {item_type}")
            return
            
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path).convert("RGBA")
                mode = self.multi_mode.get()
                
                if mode == "individual":
                    # Применяем к каждой части отдельно
                    for region_name in selected_regions:
                        regions_dict = self.cape_regions if self.cape_enabled else self.skin_regions
                        if region_name in regions_dict:
                            x1, y1, x2, y2 = self.get_scaled_region(region_name)
                            region_width = x2 - x1
                            region_height = y2 - y1
                            resized_img = img.resize((region_width, region_height), Image.LANCZOS)
                            current_image.paste(resized_img, (x1, y1), resized_img)
                
                elif mode == "stretch":
                    # Растягиваем на все выбранные части как единое целое
                    self.stretch_image_to_selected_regions(img, selected_regions)
                
                self.update_display()
                item_type = "плаща" if self.cape_enabled else "скина"
                messagebox.showinfo("Успех", f"Изображение добавлено на {len(selected_regions)} частей {item_type}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить изображение: {str(e)}")
    
    def stretch_image_to_selected_regions(self, img, regions):
        """Растягивает изображение на выбранные регионы как единое целое"""
        if not regions:
            return
            
        # Находим общие границы всех выбранных регионов
        min_x = min_y = float('inf')
        max_x = max_y = 0
        
        valid_regions = []
        for region_name in regions:
            if region_name in self.skin_regions:
                x1, y1, x2, y2 = self.get_scaled_region(region_name)
                min_x = min(min_x, x1)
                min_y = min(min_y, y1)
                max_x = max(max_x, x2)
                max_y = max(max_y, y2)
                valid_regions.append((region_name, x1, y1, x2, y2))
        
        if not valid_regions:
            return
            
        # Масштабируем изображение под общую область
        total_width = max_x - min_x
        total_height = max_y - min_y
        stretched_img = img.resize((total_width, total_height), Image.LANCZOS)
        
        # Применяем части изображения к каждому региону
        for region_name, x1, y1, x2, y2 in valid_regions:
            # Вычисляем относительные координаты в растянутом изображении
            rel_x1 = x1 - min_x
            rel_y1 = y1 - min_y
            rel_x2 = x2 - min_x
            rel_y2 = y2 - min_y
            
            # Вырезаем соответствующую часть
            region_img = stretched_img.crop((rel_x1, rel_y1, rel_x2, rel_y2))
            self.current_skin.paste(region_img, (x1, y1), region_img)
    
    def clear_selected_regions(self):
        """Очищает выбранные части скина или плаща"""
        current_image = self.current_cape if self.cape_enabled else self.current_skin
        item_type = "плаща" if self.cape_enabled else "скина"
        
        if not current_image:
            messagebox.showwarning("Предупреждение", f"Нет {item_type} для очистки")
            return
            
        selected_regions = self.get_selected_regions()
        if not selected_regions:
            messagebox.showwarning("Предупреждение", f"Выберите части {item_type}")
            return
            
        regions_dict = self.cape_regions if self.cape_enabled else self.skin_regions
        
        for region_name in selected_regions:
            if region_name in regions_dict:
                x1, y1, x2, y2 = self.get_scaled_region(region_name)
                transparent = Image.new("RGBA", (x2-x1, y2-y1), (0, 0, 0, 0))
                current_image.paste(transparent, (x1, y1))
        
        self.update_display()
        messagebox.showinfo("Успех", f"Очищено {len(selected_regions)} частей {item_type}")
    
    def show_3d_preview(self):
        """Показывает 3D превью скина"""
        if not self.current_skin:
            messagebox.showwarning("Предупреждение", "Нет скина для превью")
            return
            
        try:
            # Создаем новое окно для превью
            preview_window = tk.Toplevel(self.root)
            preview_window.title("3D Превью скина")
            preview_window.geometry("800x900")
            preview_window.resizable(True, True)
            
            # Создаем главный фрейм
            main_frame = ttk.Frame(preview_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Заголовок
            title_label = ttk.Label(main_frame, text="3D Превью скина", font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Фрейм для canvas
            canvas_frame = ttk.Frame(main_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            # Canvas для отображения превью
            preview_canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", width=760, height=800)
            preview_canvas.pack(expand=True, fill=tk.BOTH)
            
            # Генерируем 3D превью
            preview_img = self.generate_3d_preview()
            if preview_img:
                # Конвертируем PIL изображение в PhotoImage правильно
                self.preview_photo = ImageTk.PhotoImage(preview_img)
                
                # Ждем, пока canvas будет готов
                preview_window.update_idletasks()
                
                # Получаем размеры canvas после обновления
                canvas_width = preview_canvas.winfo_width()
                canvas_height = preview_canvas.winfo_height()
                
                # Если canvas еще не инициализирован, используем заданные размеры
                if canvas_width <= 1:
                    canvas_width = 760
                if canvas_height <= 1:
                    canvas_height = 800
                
                # Центрируем изображение
                x = max(0, (canvas_width - preview_img.width) // 2)
                y = max(0, (canvas_height - preview_img.height) // 2)
                
                # Отображаем изображение
                preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
                
                # Добавляем информацию
                info_text = f"Размер скина: {self.skin_size}x{self.skin_size}"
                preview_canvas.create_text(10, 10, anchor=tk.NW, text=info_text, 
                                         fill="black", font=("Arial", 12))
                
            else:
                # Если превью не создалось, показываем ошибку
                error_text = "Ошибка создания превью"
                canvas_width = preview_canvas.winfo_width() or 760
                canvas_height = preview_canvas.winfo_height() or 800
                preview_canvas.create_text(canvas_width//2, canvas_height//2, 
                                         text=error_text, fill="red", 
                                         font=("Arial", 16), anchor=tk.CENTER)
            
            # Кнопка закрытия
            close_button = ttk.Button(main_frame, text="Закрыть", 
                                    command=preview_window.destroy)
            close_button.pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать превью: {str(e)}")
            print(f"Ошибка в show_3d_preview: {e}")
            import traceback
            traceback.print_exc()
    
    def paste_with_alpha(self, target_img, source_img, position):
        """Вставляет изображение с альфа-каналом в RGB изображение"""
        if source_img.mode == 'RGBA':
            # Создаем белый фон и накладываем изображение
            bg = Image.new('RGB', source_img.size, (255, 255, 255))
            bg.paste(source_img, mask=source_img.split()[-1])
            target_img.paste(bg, position)
        else:
            target_img.paste(source_img, position)
    
    def generate_3d_preview(self):
        """Генерирует изометрическое 3D представление скина"""
        if not self.current_skin:
            return None
            
        try:
            # Размеры для превью - увеличиваем для лучшего качества
            preview_width = 700
            preview_height = 800
            
            # Создаем изображение с белым фоном (RGB вместо RGBA для лучшей совместимости)
            preview_img = Image.new("RGB", (preview_width, preview_height), (255, 255, 255))
            
            # Масштаб для отображения - увеличиваем
            scale = 16
            
            # Позиции для частей тела - центрируем
            center_x = preview_width // 2
            start_y = 80
            
            # === ГОЛОВА ===
            head_x = center_x - 4 * scale
            head_y = start_y
            
            # Получаем и обрабатываем части головы
            head_front = self.get_region_image("head_front")
            head_right = self.get_region_image("head_right") 
            head_top = self.get_region_image("head_top")
            
            # Накладываем второй слой головы если есть
            head_overlay_front = self.get_region_image("head_overlay_front")
            head_overlay_right = self.get_region_image("head_overlay_right")
            head_overlay_top = self.get_region_image("head_overlay_top")
            
            if head_front:
                # Комбинируем основной слой с наложением
                if head_overlay_front and not self.is_fully_transparent(head_overlay_front):
                    head_front = Image.alpha_composite(head_front.convert("RGBA"), head_overlay_front.convert("RGBA"))
                
                # Масштабируем и вставляем переднюю сторону
                front_scaled = head_front.resize((8*scale, 8*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, front_scaled, (head_x, head_y))
            
            if head_right:
                # Комбинируем с наложением
                if head_overlay_right and not self.is_fully_transparent(head_overlay_right):
                    head_right = Image.alpha_composite(head_right.convert("RGBA"), head_overlay_right.convert("RGBA"))
                
                # Масштабируем правую сторону (делаем уже для 3D эффекта)
                right_scaled = head_right.resize((4*scale, 8*scale), Image.NEAREST)
                # Затемняем для 3D эффекта
                right_darkened = self.darken_image(right_scaled, 0.8)
                self.paste_with_alpha(preview_img, right_darkened, (head_x + 8*scale, head_y))
            
            if head_top:
                # Комбинируем с наложением
                if head_overlay_top and not self.is_fully_transparent(head_overlay_top):
                    head_top = Image.alpha_composite(head_top.convert("RGBA"), head_overlay_top.convert("RGBA"))
                
                # Масштабируем верх (делаем ниже для 3D эффекта)
                top_scaled = head_top.resize((8*scale, 4*scale), Image.NEAREST)
                # Осветляем для 3D эффекта
                top_lightened = self.lighten_image(top_scaled, 1.1)
                self.paste_with_alpha(preview_img, top_lightened, (head_x, head_y - 4*scale))
            
            # === ТЕЛО ===
            body_x = center_x - 4 * scale
            body_y = start_y + 8 * scale
            
            body_front = self.get_region_image("body_front")
            body_right = self.get_region_image("body_right")
            
            # Накладываем куртку
            body_overlay_front = self.get_region_image("body_overlay_front")
            body_overlay_right = self.get_region_image("body_overlay_right")
            
            if body_front:
                if body_overlay_front and not self.is_fully_transparent(body_overlay_front):
                    body_front = Image.alpha_composite(body_front.convert("RGBA"), body_overlay_front.convert("RGBA"))
                
                body_front_scaled = body_front.resize((8*scale, 12*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, body_front_scaled, (body_x, body_y))
            
            if body_right:
                if body_overlay_right and not self.is_fully_transparent(body_overlay_right):
                    body_right = Image.alpha_composite(body_right.convert("RGBA"), body_overlay_right.convert("RGBA"))
                
                body_right_scaled = body_right.resize((4*scale, 12*scale), Image.NEAREST)
                body_right_darkened = self.darken_image(body_right_scaled, 0.8)
                self.paste_with_alpha(preview_img, body_right_darkened, (body_x + 8*scale, body_y))
            
            # === ПРАВАЯ РУКА ===
            arm_right_x = center_x - 12 * scale
            arm_right_y = body_y
            
            arm_right_front = self.get_region_image("arm_right_front")
            arm_right_overlay_front = self.get_region_image("arm_right_overlay_front")
            
            if arm_right_front:
                if arm_right_overlay_front and not self.is_fully_transparent(arm_right_overlay_front):
                    arm_right_front = Image.alpha_composite(arm_right_front.convert("RGBA"), arm_right_overlay_front.convert("RGBA"))
                
                arm_scaled = arm_right_front.resize((4*scale, 12*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, arm_scaled, (arm_right_x, arm_right_y))
            
            # === ЛЕВАЯ РУКА ===
            arm_left_x = center_x + 8 * scale
            arm_left_y = body_y
            
            arm_left_front = self.get_region_image("arm_left_front")
            arm_left_overlay_front = self.get_region_image("arm_left_overlay_front")
            
            if arm_left_front:
                if arm_left_overlay_front and not self.is_fully_transparent(arm_left_overlay_front):
                    arm_left_front = Image.alpha_composite(arm_left_front.convert("RGBA"), arm_left_overlay_front.convert("RGBA"))
                
                arm_scaled = arm_left_front.resize((4*scale, 12*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, arm_scaled, (arm_left_x, arm_left_y))
            
            # === ПРАВАЯ НОГА ===
            leg_right_x = center_x - 4 * scale
            leg_right_y = body_y + 12 * scale
            
            leg_right_front = self.get_region_image("leg_right_front")
            leg_right_overlay_front = self.get_region_image("leg_right_overlay_front")
            
            if leg_right_front:
                if leg_right_overlay_front and not self.is_fully_transparent(leg_right_overlay_front):
                    leg_right_front = Image.alpha_composite(leg_right_front.convert("RGBA"), leg_right_overlay_front.convert("RGBA"))
                
                leg_scaled = leg_right_front.resize((4*scale, 12*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, leg_scaled, (leg_right_x, leg_right_y))
            
            # === ЛЕВАЯ НОГА ===
            leg_left_x = center_x
            leg_left_y = body_y + 12 * scale
            
            leg_left_front = self.get_region_image("leg_left_front")
            leg_left_overlay_front = self.get_region_image("leg_left_overlay_front")
            
            if leg_left_front:
                if leg_left_overlay_front and not self.is_fully_transparent(leg_left_overlay_front):
                    leg_left_front = Image.alpha_composite(leg_left_front.convert("RGBA"), leg_left_overlay_front.convert("RGBA"))
                
                leg_scaled = leg_left_front.resize((4*scale, 12*scale), Image.NEAREST)
                self.paste_with_alpha(preview_img, leg_scaled, (leg_left_x, leg_left_y))
            
            return preview_img
            
        except Exception as e:
            print(f"Ошибка при генерации превью: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_fully_transparent(self, img):
        """Проверяет, является ли изображение полностью прозрачным"""
        if not img or img.mode != 'RGBA':
            return True
        
        try:
            # Проверяем альфа-канал
            alpha = img.split()[-1]
            extrema = alpha.getextrema()
            return extrema[1] == 0  # Максимальная прозрачность = 0
        except:
            return True
    
    def darken_image(self, img, factor):
        """Затемняет изображение"""
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def lighten_image(self, img, factor):
        """Осветляет изображение"""
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def get_region_image(self, region_name):
        """Получает изображение региона"""
        if region_name not in self.skin_regions:
            return None
            
        x1, y1, x2, y2 = self.get_scaled_region(region_name)
        return self.current_skin.crop((x1, y1, x2, y2))
    
    def show_skin_layout(self):
        """Показывает развертку скина с подписями"""
        if not self.current_skin:
            messagebox.showwarning("Предупреждение", "Нет скина для отображения")
            return
            
        # Создаем новое окно
        layout_window = tk.Toplevel(self.root)
        layout_window.title("Развертка скина")
        layout_window.geometry("800x600")
        
        # Canvas с прокруткой
        canvas_frame = ttk.Frame(layout_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        layout_canvas = tk.Canvas(canvas_frame, bg="white")
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=layout_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=layout_canvas.xview)
        
        layout_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        layout_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем изображение развертки с подписями
        layout_img = self.create_labeled_layout()
        if layout_img:
            self.layout_photo = ImageTk.PhotoImage(layout_img)
            layout_canvas.create_image(0, 0, anchor=tk.NW, image=self.layout_photo)
            layout_canvas.configure(scrollregion=layout_canvas.bbox("all"))
    
    def create_labeled_layout(self):
        """Создает развертку скина с подписями регионов"""
        if not self.current_skin:
            return None
            
        # Увеличиваем скин для лучшей видимости
        scale_factor = 8
        scaled_skin = self.current_skin.resize(
            (self.skin_size * scale_factor, self.skin_size * scale_factor), 
            Image.NEAREST
        )
        
        # Создаем изображение с местом для подписей
        layout_width = scaled_skin.width + 200
        layout_height = scaled_skin.height + 200
        layout_img = Image.new("RGB", (layout_width, layout_height), "white")
        
        # Вставляем скин
        layout_img.paste(scaled_skin, (100, 100))
        
        # Добавляем сетку и подписи
        draw = ImageDraw.Draw(layout_img)
        
        # Рисуем границы регионов и подписи
        for region_name, (x1, y1, x2, y2) in self.skin_regions.items():
            # Масштабируем координаты
            sx1 = x1 * scale_factor + 100
            sy1 = y1 * scale_factor + 100
            sx2 = x2 * scale_factor + 100
            sy2 = y2 * scale_factor + 100
            
            # Рисуем границу
            draw.rectangle([sx1, sy1, sx2-1, sy2-1], outline="red", width=2)
            
            # Добавляем подпись (только для основных частей, чтобы не загромождать)
            if any(keyword in region_name for keyword in ["front", "head_front", "body_front"]):
                text_x = sx1 + 2
                text_y = sy1 + 2
                # Упрощенная подпись
                simple_name = region_name.replace("_", " ").title()
                draw.text((text_x, text_y), simple_name[:10], fill="red")
        
        return layout_img
    
    def update_display(self):
        """Обновляет отображение скина или плаща на canvas"""
        current_image = None
        display_size = 400
        
        if self.cape_enabled and self.current_cape:
            current_image = self.current_cape
            # Для плащей используем пропорциональное масштабирование
            cape_width, cape_height = self.current_cape.size
            aspect_ratio = cape_width / cape_height
            display_width = display_size
            display_height = int(display_size / aspect_ratio)
            display_skin = self.current_cape.resize((display_width, display_height), Image.NEAREST)
        elif not self.cape_enabled and self.current_skin:
            current_image = self.current_skin
            display_skin = self.current_skin.resize((display_size, display_size), Image.NEAREST)
        else:
            return
            
        if not current_image:
            return
        
        # Создаем фон в клетку для прозрачности
        if self.cape_enabled:
            background = self.create_checkered_background(display_skin.width, display_skin.height)
        else:
            background = self.create_checkered_background(display_size, display_size)
            
        background.paste(display_skin, (0, 0), display_skin)
        
        self.skin_photo = ImageTk.PhotoImage(background)
        
        # Очищаем canvas и отображаем изображение
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # Canvas инициализирован
            x = (canvas_width - background.width) // 2
            y = (canvas_height - background.height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.skin_photo)
            
            # Рисуем сетку для лучшей видимости (только для скинов)
            if not self.cape_enabled:
                self.draw_grid(x, y, display_size)
    
    def create_checkered_background(self, width, height, square_size=10):
        """Создает фон в клетку для отображения прозрачности"""
        background = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(background)
        
        for x in range(0, width, square_size):
            for y in range(0, height, square_size):
                if (x // square_size + y // square_size) % 2:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill="#E0E0E0")
        
        return background
    
    def draw_grid(self, start_x, start_y, size):
        """Рисует сетку поверх скина"""
        grid_size = size // (self.skin_size // 8)  # 8 пикселей на клетку для 64x64
        
        for i in range(0, size + 1, grid_size):
            # Вертикальные линии
            self.canvas.create_line(start_x + i, start_y, start_x + i, start_y + size, 
                                  fill="gray", width=1, stipple="gray25")
            # Горизонтальные линии
            self.canvas.create_line(start_x, start_y + i, start_x + size, start_y + i, 
                                  fill="gray", width=1, stipple="gray25")

def main():
    root = tk.Tk()
    app = MinecraftSkinEditor(root)
    
    # Обновляем отображение после инициализации
    root.after(100, app.update_display)
    
    root.mainloop()

if __name__ == "__main__":
    main()