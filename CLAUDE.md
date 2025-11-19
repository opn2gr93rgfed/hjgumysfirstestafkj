# CLAUDE.md - AI Assistant Guide for auto2tesst

This document serves as a comprehensive guide for AI assistants (like Claude) working on the `auto2tesst` repository. It provides critical context about the codebase structure, development workflows, and conventions to follow.

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflow](#development-workflow)
4. [Key Conventions](#key-conventions)
5. [Testing Guidelines](#testing-guidelines)
6. [Git Workflow](#git-workflow)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Repository Overview

**Repository**: auto2tesst
**Status**: Active Development
**Primary Language**: Python 3.8+
**Framework/Stack**: Tkinter (GUI), Octobrowser API, Selenium

### Purpose

**Octobrowser Script Builder** - GUI-приложение конструктор для генерации Python скриптов автоматизации с использованием Octobrowser API.

**Основные цели проекта:**
- Визуальное создание скриптов автоматизации без написания boilerplate кода
- Упрощение работы с Octobrowser API
- Конструктор с чекбоксами для выбора функций (профили, прокси, fingerprints, теги)
- Генерация готовых к запуску Python скриптов
- Встроенный редактор кода для пользовательской автоматизации
- Запуск сгенерированных скриптов прямо из приложения

**Целевые пользователи:**
- Специалисты по автоматизации браузеров
- Пользователи Octobrowser, желающие автоматизировать работу с профилями
- Разработчики, создающие скрипты для веб-скрейпинга и тестирования
- Маркетологи и арбитражники, работающие с множественными профилями

**Ключевые возможности:**
- Создание и настройка профилей через API
- Генерация случайных fingerprints
- Настройка прокси (HTTP, HTTPS, SOCKS5)
- Управление тегами профилей
- Интеграция с Selenium для автоматизации
- Генерация готового Python кода
- Запуск и отладка скриптов

---

## Codebase Structure

```
auto2tesst/
├── src/                          # Исходный код приложения
│   ├── __init__.py
│   ├── api/                      # Модули работы с API
│   │   ├── __init__.py
│   │   └── octobrowser_api.py    # Класс для взаимодействия с Octobrowser API
│   ├── gui/                      # GUI интерфейс
│   │   ├── __init__.py
│   │   ├── main_window.py        # Главное окно приложения (Tkinter)
│   │   └── components/           # GUI компоненты (для будущего расширения)
│   │       └── __init__.py
│   ├── generator/                # Генератор Python скриптов
│   │   ├── __init__.py
│   │   └── script_generator.py   # Класс генерации кода из шаблонов
│   ├── runner/                   # Модуль запуска скриптов
│   │   ├── __init__.py
│   │   └── script_runner.py      # Выполнение сгенерированных скриптов
│   └── utils/                    # Утилиты и вспомогательные функции
│       └── __init__.py
├── generated_scripts/            # Папка для сгенерированных скриптов
│   └── .gitkeep
├── templates/                    # Шаблоны кода (для будущего использования)
├── config.json                   # Конфигурация (API token, настройки)
├── main.py                       # Точка входа приложения
├── requirements.txt              # Python зависимости
├── README.md                     # Руководство пользователя
├── CLAUDE.md                     # Документация для AI (этот файл)
└── .gitignore                    # Игнорируемые файлы
```

### Описание компонентов

**src/api/octobrowser_api.py** (src/api/octobrowser_api.py:1)
- Класс `OctobrowserAPI` для работы с REST API
- Методы для профилей: get_profiles, create_profile, update_profile, delete_profile, start_profile, stop_profile
- Методы для тегов: get_tags, create_tag, delete_tag
- Методы для прокси: get_proxies, create_proxy, delete_proxy
- Методы для fingerprints: get_fingerprint_settings, generate_fingerprint

**src/generator/script_generator.py** (src/generator/script_generator.py:1)
- Класс `ScriptGenerator` для генерации Python кода
- Генерация импортов, конфигурации, функций создания профиля
- Генерация кода подключения Selenium
- Генерация главной функции с пользовательским кодом
- Система приоритетов для блоков кода

**src/runner/script_runner.py** (src/runner/script_runner.py:1)
- Класс `ScriptRunner` для запуска сгенерированных скриптов
- Асинхронное и синхронное выполнение
- Callback для вывода логов в реальном времени
- Управление процессами (запуск, остановка)

**src/gui/main_window.py** (src/gui/main_window.py:1)
- Класс `OctobrowserScriptBuilder` - главное окно приложения
- Левая панель: настройки API, профилей, fingerprints, прокси, тегов
- Правая панель: редактор кода и вывод выполнения
- Кнопки: генерация, сохранение, запуск, остановка скриптов

---

## Development Workflow

### Setting Up Development Environment

**Prerequisites:**
- Python 3.8 или выше
- pip (Python package manager)
- Octobrowser установлен и имеется API токен
- Git для контроля версий

**Installation:**
```bash
# Клонирование репозитория
git clone <repository-url>
cd auto2tesst

# Установка зависимостей
pip install -r requirements.txt

# Настройка конфигурации
# Отредактировать config.json и указать API токен
```

**Зависимости:**
- `requests==2.31.0` - HTTP клиент для API запросов
- `selenium==4.15.2` - Автоматизация браузеров
- `tkinter-tooltip==2.1.0` - Подсказки для GUI
- `pillow==10.1.0` - Работа с изображениями

**Конфигурация (config.json):**
```json
{
  "octobrowser": {
    "api_base_url": "https://app.octobrowser.net/api/v2/automation",
    "api_token": "YOUR_API_TOKEN_HERE"
  },
  "script_settings": {
    "output_directory": "generated_scripts",
    "default_automation_framework": "selenium"
  }
}
```

### Running the Project

**Запуск приложения:**
```bash
python main.py
```

**Разработка:**
- Все изменения GUI делаются в `src/gui/main_window.py`
- API методы добавляются в `src/api/octobrowser_api.py`
- Генератор кода модифицируется в `src/generator/script_generator.py`

**Тестирование функционала:**
1. Запустить приложение
2. Ввести API токен и подключиться
3. Настроить параметры профиля
4. Написать тестовый код в редакторе
5. Сгенерировать скрипт
6. Запустить и проверить вывод

---

## Key Conventions

### Code Style

**Python Style Guide (PEP 8):**
- **Indentation**: 4 пробела
- **Line Length**: Максимум 120 символов
- **Encoding**: UTF-8
- **Imports**: Группируются (stdlib, third-party, local)
- **Docstrings**: Google style для всех классов и публичных методов

**Naming Conventions:**
- **Classes**: `PascalCase` (например, `OctobrowserAPI`, `ScriptGenerator`)
- **Functions/Methods**: `snake_case` (например, `create_profile`, `generate_script`)
- **Variables**: `snake_case` (например, `api_token`, `profile_data`)
- **Constants**: `UPPER_SNAKE_CASE` (например, `API_BASE_URL`)
- **Private**: Префикс `_` (например, `_make_request`, `_generate_header`)

**Comments:**
- Документируйте "почему", а не "что"
- Используйте docstrings для всех публичных API
- Комментарии на русском для внутренней логики, на английском для API

**Type Hints:**
- Используйте type hints для параметров функций
- Используйте `Optional`, `Dict`, `List` из typing
- Пример: `def create_profile(self, profile_data: Dict) -> Dict:`

### File Organization

**Naming Patterns:**
- Python модули: `lowercase_with_underscores.py`
- Классы: Один основной класс на файл
- Конфигурация: JSON формат, `config.json`
- Скрипты: `automation_script_YYYYMMDD_HHMMSS.py`

**Module Structure:**
- `__init__.py` в каждом пакете
- Импорты абсолютные от корня проекта
- Избегать циклических зависимостей

**Generated Scripts:**
- Сохраняются в `generated_scripts/`
- Имеют timestamp в имени
- Содержат полный автономный код

### Dependencies

**Adding Dependencies:**
```bash
# Установить новый пакет
pip install package_name

# Обновить requirements.txt
pip freeze > requirements.txt
```

**Version Pinning:**
- Использовать точные версии для стабильности
- Формат: `package==version`
- Регулярно проверять обновления безопасности

**Dependency Updates:**
1. Проверить changelog пакета
2. Тестировать в dev среде
3. Обновить requirements.txt
4. Документировать breaking changes

---

## Testing Guidelines

### Testing Strategy

Document the testing approach:
- **Unit Tests**: What to test, coverage expectations
- **Integration Tests**: Component interaction testing
- **E2E Tests**: User flow testing
- **Test Location**: Where tests should be placed

### Running Tests

Commands and procedures for:
- Running all tests
- Running specific test suites
- Running tests in watch mode
- Generating coverage reports

### Writing Tests

- Test naming conventions
- Test structure patterns
- Mocking/stubbing guidelines
- Test data management

---

## Git Workflow

### Branch Strategy

**Feature Branch Workflow**:
- Main/master branch: Production-ready code
- Feature branches: Named `claude/<description>-<session-id>`
- Development branches: As specified per task

### Commit Guidelines

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Best Practices**:
- Keep commits atomic and focused
- Write clear, descriptive commit messages
- Reference issues/PRs when relevant
- Avoid committing sensitive data (.env files, credentials)

### Push Protocol

When pushing changes:
1. Review changes with `git status` and `git diff`
2. Stage relevant files
3. Commit with descriptive message
4. Push to feature branch: `git push -u origin <branch-name>`
5. Retry with exponential backoff if network errors occur

---

## Common Tasks

### Adding a New Feature

1. Create/checkout feature branch
2. Implement the feature with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Commit changes
6. Push to remote branch
7. Create pull request (if applicable)

### Fixing a Bug

1. Identify and reproduce the bug
2. Write a failing test that demonstrates the bug
3. Fix the bug
4. Ensure the test passes
5. Ensure all other tests still pass
6. Commit and push

### Updating Dependencies

1. Check for outdated dependencies
2. Review changelogs for breaking changes
3. Update dependency versions
4. Run full test suite
5. Update documentation if APIs changed
6. Commit changes

### Refactoring

1. Ensure comprehensive test coverage exists
2. Make incremental changes
3. Run tests after each change
4. Keep commits small and focused
5. Document any API changes

---

## Troubleshooting

### Common Issues

This section will be populated as common issues arise. Document:
- Issue description
- Root cause
- Solution/workaround
- Prevention strategies

### Debug Strategies

When investigating issues:
1. Reproduce the problem consistently
2. Isolate the failing component
3. Check recent changes (git log, git diff)
4. Review relevant logs
5. Add debug logging if needed
6. Test fixes incrementally

---

## AI Assistant Specific Guidelines

### Code Analysis

When analyzing this codebase:
1. Use the Explore agent for comprehensive codebase exploration
2. Use Grep for targeted searches within known areas
3. Use Glob for finding files by pattern
4. Read relevant documentation files first

### Task Planning

For complex tasks:
1. Use TodoWrite to plan and track progress
2. Break down large tasks into smaller steps
3. Mark todos as in_progress before starting
4. Mark todos as completed immediately after finishing
5. Keep only one todo in_progress at a time

### Code Modifications

When modifying code:
1. Always read files before editing
2. Prefer Edit tool over Write for existing files
3. Maintain existing code style and patterns
4. Add tests for new functionality
5. Run tests before committing
6. Never commit files with secrets or credentials

### Security Considerations

Always consider:
- Input validation and sanitization
- SQL injection prevention
- XSS prevention
- CSRF protection
- Authentication and authorization
- Secure credential handling
- OWASP Top 10 vulnerabilities

---

## Project Evolution

As this project grows, update this document to reflect:
- New architectural decisions
- Technology stack choices
- Design patterns adopted
- Integration patterns
- Deployment procedures
- Monitoring and logging approaches
- Performance optimization strategies

---

## Notes for AI Assistants

### Communication Style

- Be concise and direct
- Use technical accuracy over validation
- Avoid emojis unless explicitly requested
- Focus on problem-solving
- Provide objective guidance

### Tool Usage

- Prefer specialized tools over bash commands for file operations
- Run independent operations in parallel when possible
- Use Task tool for complex, multi-step operations
- Use appropriate agents (Explore, Plan) for their specialized purposes

### Best Practices

- Always verify file paths before operations
- Check for existing patterns before introducing new ones
- Consider backward compatibility
- Document significant decisions
- Test thoroughly before committing
- Ask for clarification when requirements are ambiguous

---

## Maintenance

**Last Updated**: 2025-11-15
**Updated By**: Claude (Full project implementation)

**Update Triggers**:
- Major architectural changes
- New technology adoption
- Significant workflow changes
- Common issues discovered
- New team conventions established

---

## Additional Resources

### Octobrowser API

**Официальная документация:**
- Swagger API: https://swagger.octobrowser.net/
- Postman Collection: https://documenter.getpostman.com/view/1801428/UVC6i6eA
- Официальные docs: https://docs.octobrowser.net/
- API FAQ: https://docs.octobrowser.net/en/faq/api-faq/

**Base URL:** `https://app.octobrowser.net/api/v2/automation`

**Аутентификация:**
- Header: `X-Octo-Api-Token: YOUR_TOKEN`
- Токен находится в Octobrowser → Настройки → Вкладка "Дополнительно"

**Rate Limits:**
- Base: 50 RPM / 500 RPH
- Team: 100 RPM / 1,500 RPH
- Advanced: 200+ RPM / 3,000+ RPH

**Основные endpoints:**
- `GET /profiles` - Список профилей
- `POST /profiles` - Создать профиль
- `GET /profiles/{uuid}` - Получить профиль
- `PATCH /profiles/{uuid}` - Обновить профиль
- `DELETE /profiles/{uuid}` - Удалить профиль
- `POST /profiles/{uuid}/start` - Запустить профиль
- `POST /profiles/{uuid}/stop` - Остановить профиль
- `GET /tags` - Получить теги
- `POST /tags` - Создать тег
- `GET /proxies` - Получить прокси
- `POST /proxies` - Добавить прокси

### External Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [PEP 8 Style Guide](https://pep8.org/)

### Project Resources

- README.md - Полное руководство пользователя
- config.json - Файл конфигурации
- generated_scripts/ - Примеры сгенерированных скриптов
