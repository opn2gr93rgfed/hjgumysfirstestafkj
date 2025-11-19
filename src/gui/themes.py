"""
🎨 Modern Themes для auto2tesst v2
Стильные цветовые схемы 2025 года
"""

class ModernTheme:
    """Современная темная тема с градиентами и анимациями"""

    # === DARK THEME (По умолчанию) ===
    DARK = {
        # Основные цвета фона
        'bg_primary': '#0a0e27',      # Глубокий темно-синий фон
        'bg_secondary': '#151932',    # Вторичный фон (карточки)
        'bg_tertiary': '#1e2343',     # Третичный фон (input fields)
        'bg_hover': '#252b4f',        # Hover эффект
        'bg_sidebar': '#0d1128',      # Сайдбар (еще темнее)

        # Акцентные цвета
        'accent_primary': '#6366f1',   # Яркий индиго (главные кнопки)
        'accent_secondary': '#8b5cf6', # Фиолетовый (второстепенные)
        'accent_success': '#10b981',   # Зеленый (успех)
        'accent_warning': '#f59e0b',   # Оранжевый (предупреждение)
        'accent_error': '#ef4444',     # Красный (ошибка)
        'accent_info': '#3b82f6',      # Синий (инфо)

        # Градиенты
        'gradient_primary': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'gradient_success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        'gradient_error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',

        # Текст
        'text_primary': '#f8fafc',     # Основной текст (почти белый)
        'text_secondary': '#94a3b8',   # Второстепенный текст (серый)
        'text_tertiary': '#64748b',    # Третичный текст (темнее)
        'text_disabled': '#475569',    # Отключенный текст
        'text_on_accent': '#ffffff',   # Текст на акцентных кнопках

        # Границы
        'border_primary': '#1e293b',   # Основные границы
        'border_secondary': '#334155', # Второстепенные границы
        'border_accent': '#6366f1',    # Акцентные границы

        # Тени
        'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
        'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
        'shadow_xl': '0 20px 25px -5px rgba(0, 0, 0, 0.6)',
        'shadow_glow': '0 0 20px rgba(99, 102, 241, 0.5)',  # Светящаяся тень

        # Специальные цвета для логов
        'log_info': '#60a5fa',         # Синий для [INFO]
        'log_success': '#34d399',      # Зеленый для [OK], [SUCCESS]
        'log_warning': '#fbbf24',      # Желтый для [WARNING]
        'log_error': '#f87171',        # Красный для [ERROR]
        'log_smart': '#a78bfa',        # Фиолетовый для [SMART CLICK]
        'log_answer': '#2dd4bf',       # Бирюзовый для [ANSWER]
        'log_random': '#fb923c',       # Оранжевый для [RANDOM]
        'log_popup': '#c084fc',        # Лиловый для [POPUP]
    }

    # === LIGHT THEME ===
    LIGHT = {
        # Основные цвета фона
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_tertiary': '#f1f5f9',
        'bg_hover': '#e2e8f0',
        'bg_sidebar': '#f9fafb',

        # Акцентные цвета
        'accent_primary': '#6366f1',
        'accent_secondary': '#8b5cf6',
        'accent_success': '#10b981',
        'accent_warning': '#f59e0b',
        'accent_error': '#ef4444',
        'accent_info': '#3b82f6',

        # Текст
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_tertiary': '#64748b',
        'text_disabled': '#cbd5e1',
        'text_on_accent': '#ffffff',

        # Границы
        'border_primary': '#e2e8f0',
        'border_secondary': '#cbd5e1',
        'border_accent': '#6366f1',

        # Тени
        'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'shadow_xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        'shadow_glow': '0 0 20px rgba(99, 102, 241, 0.3)',

        # Логи
        'log_info': '#3b82f6',
        'log_success': '#10b981',
        'log_warning': '#f59e0b',
        'log_error': '#ef4444',
        'log_smart': '#8b5cf6',
        'log_answer': '#14b8a6',
        'log_random': '#f97316',
        'log_popup': '#a855f7',
    }

    # === РАЗМЕРЫ И SPACING ===
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }

    RADIUS = {
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
        'full': 9999,
    }

    FONT = {
        'family': ('Segoe UI', 'SF Pro Display', 'Helvetica Neue', 'Arial'),
        'size_xs': 10,
        'size_sm': 12,
        'size_md': 14,
        'size_lg': 16,
        'size_xl': 20,
        'size_xxl': 24,
        'size_hero': 32,
    }

    # === ИКОНКИ (Unicode эмодзи для кроссплатформенности) ===
    ICONS = {
        # Навигация
        'import': '📥',
        'run': '▶️',
        'stop': '⏹️',
        'logs': '📋',
        'settings': '⚙️',

        # Действия
        'save': '💾',
        'open': '📂',
        'clear': '🗑️',
        'edit': '✏️',
        'copy': '📋',

        # Статусы
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳',

        # Утилиты
        'expand': '▼',
        'collapse': '▲',
        'close': '✕',
        'search': '🔍',
        'theme': '🌙',
        'drag': '📎',
    }

    @classmethod
    def get_theme(cls, mode='dark'):
        """Получить тему по названию"""
        return cls.DARK if mode == 'dark' else cls.LIGHT

    @classmethod
    def get_ctk_colors(cls, mode='dark'):
        """
        Получить цвета в формате CustomTkinter
        Returns: dict для set_default_color_theme()
        """
        theme = cls.get_theme(mode)
        return {
            'CTkFrame': {
                'fg_color': theme['bg_secondary'],
                'border_color': theme['border_primary'],
            },
            'CTkButton': {
                'fg_color': theme['accent_primary'],
                'hover_color': theme['bg_hover'],
                'text_color': theme['text_on_accent'],
                'border_color': theme['border_accent'],
            },
            'CTkEntry': {
                'fg_color': theme['bg_tertiary'],
                'border_color': theme['border_primary'],
                'text_color': theme['text_primary'],
            },
            'CTkTextbox': {
                'fg_color': theme['bg_tertiary'],
                'border_color': theme['border_primary'],
                'text_color': theme['text_primary'],
            },
        }


# === PRESETS для компонентов ===

class ButtonStyles:
    """Стили для кнопок"""

    PRIMARY = {
        'corner_radius': ModernTheme.RADIUS['lg'],
        'height': 44,
        'font_size': ModernTheme.FONT['size_md'],
        'border_width': 0,
    }

    LARGE = {
        'corner_radius': ModernTheme.RADIUS['xl'],
        'height': 56,
        'font_size': ModernTheme.FONT['size_lg'],
        'border_width': 0,
    }

    SMALL = {
        'corner_radius': ModernTheme.RADIUS['md'],
        'height': 32,
        'font_size': ModernTheme.FONT['size_sm'],
        'border_width': 0,
    }


class AnimationConfig:
    """Конфигурация анимаций"""

    FAST = 150      # мс
    NORMAL = 300    # мс
    SLOW = 500      # мс

    EASING = 'ease-out'  # Тип анимации


# === ГОТОВЫЕ CTK ТЕМЫ ===

# Темная тема для CustomTkinter
CTK_DARK_THEME = {
    "CTk": {
        "fg_color": ModernTheme.DARK['bg_primary']
    },
    "CTkToplevel": {
        "fg_color": ModernTheme.DARK['bg_primary']
    },
    "CTkFrame": {
        "corner_radius": ModernTheme.RADIUS['lg'],
        "border_width": 1,
        "fg_color": ModernTheme.DARK['bg_secondary'],
        "border_color": ModernTheme.DARK['border_primary']
    },
    "CTkButton": {
        "corner_radius": ModernTheme.RADIUS['lg'],
        "border_width": 0,
        "fg_color": ModernTheme.DARK['accent_primary'],
        "hover_color": ModernTheme.DARK['bg_hover'],
        "text_color": ModernTheme.DARK['text_on_accent'],
        "font": (ModernTheme.FONT['family'], ModernTheme.FONT['size_md'])
    },
    "CTkEntry": {
        "corner_radius": ModernTheme.RADIUS['md'],
        "border_width": 1,
        "fg_color": ModernTheme.DARK['bg_tertiary'],
        "border_color": ModernTheme.DARK['border_primary'],
        "text_color": ModernTheme.DARK['text_primary'],
        "placeholder_text_color": ModernTheme.DARK['text_tertiary']
    },
    "CTkTextbox": {
        "corner_radius": ModernTheme.RADIUS['md'],
        "border_width": 1,
        "fg_color": ModernTheme.DARK['bg_tertiary'],
        "border_color": ModernTheme.DARK['border_primary'],
        "text_color": ModernTheme.DARK['text_primary']
    },
    "CTkSwitch": {
        "corner_radius": ModernTheme.RADIUS['full'],
        "border_width": 3,
        "button_color": ModernTheme.DARK['bg_primary'],
        "fg_color": ModernTheme.DARK['border_secondary'],
        "progress_color": ModernTheme.DARK['accent_primary'],
        "button_hover_color": ModernTheme.DARK['bg_hover']
    },
    "CTkCheckBox": {
        "corner_radius": ModernTheme.RADIUS['sm'],
        "border_width": 2,
        "fg_color": ModernTheme.DARK['accent_primary'],
        "border_color": ModernTheme.DARK['border_secondary'],
        "hover_color": ModernTheme.DARK['bg_hover'],
        "text_color": ModernTheme.DARK['text_primary']
    },
    "CTkProgressBar": {
        "corner_radius": ModernTheme.RADIUS['full'],
        "border_width": 0,
        "fg_color": ModernTheme.DARK['bg_tertiary'],
        "progress_color": ModernTheme.DARK['accent_primary']
    },
}
