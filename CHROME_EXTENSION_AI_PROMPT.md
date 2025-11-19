# 🔧 ПРОМПТ ДЛЯ AI: Исправление Chrome Extension "Selenium Chrome Recorder"

## 📍 Контекст задачи

Ты работаешь над Chrome Extension в репозитории:
**https://github.com/joffreu243-png/auto2tesst/tree/claude/selenium-chrome-recorder-01GicDYm6tqRxTJmUiCLuU54/chrome-extension**

Этот Extension записывает действия пользователя и генерирует Python Selenium код для приложения **auto2tesst**.

### ⚠️ ТЕКУЩИЕ ПРОБЛЕМЫ

Extension генерирует **НЕРАБОТАЮЩИЙ КОД** с критическими багами:

1. ❌ **Отсутствует `driver.get()` в начале** - код не открывает страницу
2. ❌ **Дублирование `send_keys()`** - каждая буква записывается отдельно
3. ❌ **Переменные без кавычек** - использует `search` вместо `"{{search}}"`
4. ❌ **Плохие селекторы** - длинные XPath и `:nth-child()` вместо ID/NAME
5. ❌ **Избыточные действия** - клики перед вводом текста, лишние navigate
6. ❌ **Текст элементов в коде** - появляются строки без кавычек

### 📚 ПОЛНАЯ СПЕЦИФИКАЦИЯ

**ОБЯЗАТЕЛЬНО ПРОЧИТАЙ:**
`/home/user/auto2tesst/CHROME_EXTENSION_COMPLETE_SPEC.md` - 500+ строк детальной документации с примерами кода, алгоритмами и требованиями.

---

## 🎯 ЧТО НУЖНО ИСПРАВИТЬ

### 1. Файл: `content/content.js` - Event Listener

**ПРОБЛЕМА:** Записывает каждое нажатие клавиши отдельно

**ТЕКУЩИЙ КОД (ПЛОХО):**
```javascript
handleInput(event) {
    this.addAction({
        type: 'type',
        value: event.target.value  // Записывает после КАЖДОЙ буквы
    });
}
```

**ИСПРАВЛЕННЫЙ КОД (ХОРОШО):**
```javascript
constructor() {
    // ... другие поля
    this.typeTimeout = null;           // ✅ Добавить debounce
    this.currentTypeElement = null;
    this.currentTypeValue = '';
}

handleInput(event) {
    const element = event.target;

    // Очистить предыдущий таймер
    if (this.typeTimeout) {
        clearTimeout(this.typeTimeout);
    }

    // Сохранить элемент и значение
    this.currentTypeElement = element;
    this.currentTypeValue = element.value;

    // Ждать 500ms после последнего нажатия
    this.typeTimeout = setTimeout(() => {
        if (this.currentTypeElement) {
            this.addAction({
                type: 'type',
                element: this.currentTypeElement,
                value: this.currentTypeValue,  // ✅ Полное значение, не каждая буква
                selector: SelectorGenerator.generate(this.currentTypeElement),
                timestamp: Date.now(),
                url: window.location.href
            });

            this.currentTypeElement = null;
            this.currentTypeValue = '';
        }
    }, 500);  // 500ms debounce
}
```

**ЧТО ДЕЛАТЬ:**
- ✅ Добавить debounce таймер (500ms) для объединения нажатий клавиш
- ✅ Сохранять элемент и накапливать значение
- ✅ Записывать действие только после паузы 500ms
- ✅ Записывать полное значение поля, а не каждую букву

---

### 2. Файл: `recorder/selector-generator.js` - Selector Generator

**ПРОБЛЕМА:** Генерирует сложные XPath и CSS с `:nth-child()` вместо простых ID/NAME

**ТЕКУЩИЙ КОД (ПЛОХО):**
```javascript
// Использует nth-child слишком часто
selector += `:nth-child(${index})`;
```

**ИСПРАВЛЕННЫЙ КОД (ХОРОШО):**
```javascript
static generate(element) {
    if (!element || !(element instanceof Element)) {
        return null;
    }

    // ✅ Приоритет 1: ID (самый надежный)
    if (element.id) {
        return {
            type: 'id',
            value: element.id,
            by: 'By.ID',
            selector: element.id
        };
    }

    // ✅ Приоритет 2: NAME (для форм)
    if (element.name) {
        return {
            type: 'name',
            value: element.name,
            by: 'By.NAME',
            selector: element.name
        };
    }

    // ✅ Приоритет 3: data-testid, data-test, data-qa
    const testAttrs = ['data-testid', 'data-test-id', 'data-test', 'data-qa', 'data-cy'];
    for (const attr of testAttrs) {
        const value = element.getAttribute(attr);
        if (value) {
            return {
                type: 'css',
                value: `[${attr}="${value}"]`,
                by: 'By.CSS_SELECTOR',
                selector: `[${attr}="${value}"]`
            };
        }
    }

    // ✅ Приоритет 4: XPath с текстом (ТОЛЬКО для кнопок/ссылок)
    if (['A', 'BUTTON'].includes(element.tagName)) {
        const text = element.textContent.trim().substring(0, 30);
        if (text) {
            const tag = element.tagName.toLowerCase();
            const xpath = `//${tag}[contains(text(), "${text}")]`;
            return {
                type: 'xpath',
                value: xpath,
                by: 'By.XPATH',
                selector: xpath
            };
        }
    }

    // ⚠️ ПОСЛЕДНИЙ ШАНС: Простой CSS БЕЗ nth-child
    // Используйте nth-child ТОЛЬКО если нет другого выбора
    const cssSelector = this.buildSimpleCssSelector(element);
    return {
        type: 'css',
        value: cssSelector,
        by: 'By.CSS_SELECTOR',
        selector: cssSelector
    };
}

// ✅ Новый метод: строить простой CSS без nth-child
static buildSimpleCssSelector(element) {
    // Попробовать tag + class
    if (element.className) {
        const classes = element.className.split(' ')
            .filter(c => c.trim() && !c.match(/^(hover|active|focus)/))
            .slice(0, 2);

        if (classes.length > 0) {
            return `${element.tagName.toLowerCase()}.${classes.join('.')}`;
        }
    }

    // Попробовать tag + type/placeholder
    if (element.type) {
        return `${element.tagName.toLowerCase()}[type="${element.type}"]`;
    }

    if (element.placeholder) {
        return `${element.tagName.toLowerCase()}[placeholder="${element.placeholder}"]`;
    }

    // Последний вариант: просто тег (может быть не уникальным!)
    return element.tagName.toLowerCase();
}
```

**ЧТО ДЕЛАТЬ:**
- ✅ ВСЕГДА проверять ID и NAME первыми
- ✅ Проверять data-testid, data-test, data-qa атрибуты
- ✅ Использовать XPath с текстом ТОЛЬКО для кнопок и ссылок
- ❌ ИЗБЕГАТЬ `:nth-child()` и `:nth-of-type()` - использовать только когда нет выбора
- ✅ Предпочитать простые селекторы сложным

---

### 3. Файл: `generator/selenium-generator.js` - Selenium Code Generator

**ПРОБЛЕМА 1:** Код для auto2tesst не начинается с `driver.get()`

**ИСПРАВЛЕНИЕ метода `generateForAuto2tesst()`:**

```javascript
generateForAuto2tesst(actions) {
    if (!actions || actions.length === 0) {
        return '# Нет записанных действий\nprint("Действия не записаны")';
    }

    // ✅ КРИТИЧЕСКИ ВАЖНО: Оптимизировать действия
    const optimizedActions = this.optimizeActions(actions);

    let code = '';

    // ✅ ОБЯЗАТЕЛЬНО: Начинаем с driver.get()
    const firstUrl = optimizedActions[0]?.url || 'https://example.com';
    code += `# Переход на страницу\n`;
    code += `driver.get("${firstUrl}")\n`;
    code += `time.sleep(2)\n\n`;

    // ✅ Генерировать действия
    for (let i = 0; i < optimizedActions.length; i++) {
        const action = optimizedActions[i];

        // Пропустить первый navigate (уже сделали driver.get выше)
        if (i === 0 && action.type === 'navigate') {
            continue;
        }

        const actionCode = this.generateAction(action, i);
        if (actionCode) {
            code += actionCode + '\n';
        }
    }

    return code;
}
```

**ПРОБЛЕМА 2:** Переменные без кавычек (`search` вместо `"{{search}}"`)

**ИСПРАВЛЕНИЕ метода `escapeString()`:**

```javascript
escapeString(str) {
    if (!str) return '';

    // ✅ ВАЖНО: Если строка выглядит как переменная (например "email", "password")
    // НО не имеет синтаксиса {{variable}}, НЕ ТРОГАЕМ ЕЁ - это пользовательские данные

    // ✅ Правильное экранирование:
    return str
        .replace(/\\/g, '\\\\')   // Backslash
        .replace(/"/g, '\\"')      // Двойные кавычки
        .replace(/'/g, "\\'")      // Одинарные кавычки
        .replace(/\n/g, '\\n')     // Новая строка
        .replace(/\r/g, '\\r')     // Возврат каретки
        .replace(/\t/g, '\\t');    // Табуляция
}
```

**ИСПРАВЛЕНИЕ метода `generateTypeAction()`:**

```javascript
generateTypeAction(action) {
    const selector = action.selector;
    let value = action.value || '';

    // ✅ ВАЖНО: Все значения должны быть в кавычках с синтаксисом {{variable}}
    // Если пользователь ввел "email@example.com", генерируем:
    // element.send_keys("{{email}}")  - с параметризацией

    // Для auto2tesst ВСЕГДА используем синтаксис "{{переменная}}"
    const varName = this.sanitizeVariableName(value);
    const escapedValue = `"{{${varName}}}"`;  // ✅ Всегда в кавычках!

    let code = '';
    code += `# Ввод текста в поле\n`;
    code += `element = WebDriverWait(driver, 10).until(\n`;
    code += `    EC.presence_of_element_located((${selector.by}, "${this.escapeString(selector.selector)}"))\n`;
    code += `)\n`;
    code += `element.send_keys(${escapedValue})\n`;  // ✅ "{{variable}}"
    code += `print(f"Введено значение в поле")\n`;
    code += `time.sleep(1)\n`;

    return code;
}

// ✅ Новый метод: преобразовать значение в имя переменной
sanitizeVariableName(value) {
    if (!value) return 'value';

    // Если значение похоже на email
    if (value.includes('@')) return 'email';

    // Если значение похоже на пароль
    if (value.length >= 8 && /[A-Z]/.test(value) && /[0-9]/.test(value)) {
        return 'password';
    }

    // Общий случай: первые 10 символов
    return value.substring(0, 10)
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '_')
        .replace(/^[0-9]/, 'var_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '') || 'value';
}
```

**ПРОБЛЕМА 3:** Не удаляются избыточные действия

**ИСПРАВЛЕНИЕ метода `optimizeActions()`:**

```javascript
optimizeActions(actions) {
    if (!actions || actions.length === 0) return [];

    let optimized = [...actions];

    // ✅ ШАГ 1: Объединить последовательные send_keys к одному полю
    optimized = this.combineSequentialTypes(optimized);

    // ✅ ШАГ 2: Удалить клики перед вводом текста (избыточны)
    optimized = this.removeClicksBeforeType(optimized);

    // ✅ ШАГ 3: Удалить navigate после submit/click (избыточны)
    optimized = this.removeRedundantNavigates(optimized);

    return optimized;
}

// ✅ Новый метод: объединить последовательные вводы в одно поле
combineSequentialTypes(actions) {
    const result = [];
    let i = 0;

    while (i < actions.length) {
        const current = actions[i];

        if (current.type === 'type') {
            // Найти все последующие type в тот же элемент
            let combinedValue = current.value;
            let j = i + 1;

            while (j < actions.length &&
                   actions[j].type === 'type' &&
                   actions[j].selector?.selector === current.selector?.selector) {
                // ✅ ВАЖНО: Берем ПОСЛЕДНЕЕ значение (финальное состояние поля)
                combinedValue = actions[j].value;
                j++;
            }

            // Добавить объединенное действие
            result.push({
                ...current,
                value: combinedValue  // ✅ Финальное значение
            });

            i = j;  // Пропустить обработанные действия
        } else {
            result.push(current);
            i++;
        }
    }

    return result;
}

// ✅ Новый метод: удалить клики перед вводом текста
removeClicksBeforeType(actions) {
    const result = [];

    for (let i = 0; i < actions.length; i++) {
        const current = actions[i];
        const next = actions[i + 1];

        // Если это клик и следующее действие - ввод в тот же элемент
        if (current.type === 'click' &&
            next?.type === 'type' &&
            current.selector?.selector === next.selector?.selector) {
            // ✅ Пропустить клик (он избыточен)
            continue;
        }

        result.push(current);
    }

    return result;
}

// ✅ Новый метод: удалить navigate после submit/click
removeRedundantNavigates(actions) {
    const result = [];

    for (let i = 0; i < actions.length; i++) {
        const current = actions[i];
        const prev = actions[i - 1];

        // Если это navigate и предыдущее действие - submit или клик по ссылке
        if (current.type === 'navigate' && prev) {
            if (prev.type === 'submit') {
                // ✅ Пропустить navigate после submit
                continue;
            }

            if (prev.type === 'click' && prev.element?.tagName === 'A') {
                // ✅ Пропустить navigate после клика по ссылке
                continue;
            }
        }

        result.push(current);
    }

    return result;
}
```

---

## ✅ КРИТЕРИИ ПРИЕМКИ

### Тест 1: Поиск в Google

**Действия пользователя:**
1. Открыть https://www.google.com
2. Ввести в поле поиска "vodka"
3. Нажать Enter

**Ожидаемый сгенерированный код:**
```python
# Переход на страницу
driver.get("https://www.google.com")
time.sleep(2)

# Ввод текста в поле
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "q"))
)
element.send_keys("{{search_query}}")
print(f"Введено значение в поле")
time.sleep(1)

# Отправка формы
element.submit()
print("Форма отправлена")
time.sleep(2)
```

**Проверки:**
- ✅ Есть `driver.get()` в начале
- ✅ Используется `By.NAME` (а не XPath или nth-child)
- ✅ Значение в кавычках: `"{{search_query}}"`
- ✅ Только ОДИН `send_keys()` (не дублируется для каждой буквы)
- ✅ Нет избыточных кликов
- ✅ Нет импортов

---

### Тест 2: Регистрация (форма)

**Действия пользователя:**
1. Открыть https://example.com/register
2. Ввести в поле "First Name": "John"
3. Ввести в поле "Last Name": "Doe"
4. Ввести в поле "Email": "john@example.com"
5. Нажать кнопку "Sign Up"

**Ожидаемый код:**
```python
# Переход на страницу
driver.get("https://example.com/register")
time.sleep(2)

# Ввод текста в поле
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "firstName"))
)
element.send_keys("{{firstname}}")
print(f"Введено значение в поле")
time.sleep(1)

# Ввод текста в поле
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "lastName"))
)
element.send_keys("{{lastname}}")
print(f"Введено значение в поле")
time.sleep(1)

# Ввод текста в поле
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)
element.send_keys("{{email}}")
print(f"Введено значение в поле")
time.sleep(1)

# Клик по кнопке
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign Up')]"))
)
element.click()
print("Выполнен клик по кнопке")
time.sleep(2)
```

**Проверки:**
- ✅ Есть `driver.get()` в начале
- ✅ Используются ID для полей
- ✅ XPath только для кнопки (у неё нет ID)
- ✅ Все значения: `"{{variable}}"` в кавычках
- ✅ По одному `send_keys()` на каждое поле
- ✅ Нет кликов перед send_keys

---

### Тест 3: Поиск в Wikipedia

**Действия:**
1. Открыть https://en.wikipedia.org
2. Ввести "Python programming" в поиск
3. Кликнуть на первый результат

**Ожидаемый код:**
```python
# Переход на страницу
driver.get("https://en.wikipedia.org")
time.sleep(2)

# Ввод текста в поле
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "search"))
)
element.send_keys("{{search_query}}")
print(f"Введено значение в поле")
time.sleep(1)

# Клик по кнопке
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
)
element.click()
print("Выполнен клик по кнопке")
time.sleep(2)
```

**Проверки:**
- ✅ Есть `driver.get()` в начале
- ✅ Используется `By.NAME` для поля поиска
- ✅ Значение поиска: `"{{search_query}}"`
- ✅ Один `send_keys()` со всем текстом
- ✅ Нет лишних navigate после клика

---

## 📋 ЧЕКЛИСТ РАЗРАБОТКИ

### Этап 1: Анализ текущего кода
- [ ] Прочитать `/home/user/auto2tesst/CHROME_EXTENSION_COMPLETE_SPEC.md`
- [ ] Изучить структуру Extension
- [ ] Найти все проблемные места в коде
- [ ] Составить план исправлений

### Этап 2: Исправление Event Listener
- [ ] Добавить debounce (500ms) для объединения нажатий клавиш
- [ ] Исправить `handleInput()` в `content/content.js`
- [ ] Протестировать: ввод текста записывается один раз

### Этап 3: Исправление Selector Generator
- [ ] Реализовать приоритет: ID > NAME > data-test > XPath > CSS
- [ ] Избегать `:nth-child()` без крайней необходимости
- [ ] Исправить `recorder/selector-generator.js`
- [ ] Протестировать на разных элементах

### Этап 4: Исправление Code Generator
- [ ] Добавить `driver.get()` в начало для auto2tesst
- [ ] Исправить синтаксис переменных: `"{{variable}}"`
- [ ] Реализовать `combineSequentialTypes()`
- [ ] Реализовать `removeClicksBeforeType()`
- [ ] Реализовать `removeRedundantNavigates()`
- [ ] Исправить `generator/selenium-generator.js`

### Этап 5: Тестирование
- [ ] Тест 1: Поиск в Google (базовый тест)
- [ ] Тест 2: Форма регистрации (множество полей)
- [ ] Тест 3: Wikipedia (сложные селекторы)
- [ ] Проверить весь код на отсутствие импортов
- [ ] Проверить все значения в кавычках

### Этап 6: Приемка
- [ ] Все 3 теста проходят успешно
- [ ] Код валидный Python
- [ ] Нет дублирования действий
- [ ] Используются надежные селекторы
- [ ] Готово к использованию в auto2tesst

---

## 🎓 ВАЖНЫЕ НАПОМИНАНИЯ

### ❌ ЧТО НЕ ДЕЛАТЬ:

1. **НЕ добавлять импорты в генерируемый код**
   ```python
   # ❌ НЕПРАВИЛЬНО
   from selenium.webdriver.common.by import By
   ```

2. **НЕ использовать переменные без кавычек**
   ```python
   # ❌ НЕПРАВИЛЬНО
   element.send_keys(email)

   # ✅ ПРАВИЛЬНО
   element.send_keys("{{email}}")
   ```

3. **НЕ записывать каждое нажатие клавиши**
   ```python
   # ❌ НЕПРАВИЛЬНО
   element.send_keys("J")
   element.send_keys("o")
   element.send_keys("h")
   element.send_keys("n")

   # ✅ ПРАВИЛЬНО
   element.send_keys("{{name}}")
   ```

4. **НЕ использовать `:nth-child()` без необходимости**
   ```python
   # ❌ НЕПРАВИЛЬНО
   By.CSS_SELECTOR, "div:nth-child(3) > input:nth-child(1)"

   # ✅ ПРАВИЛЬНО
   By.ID, "email"
   ```

5. **НЕ пропускать `driver.get()` в начале**
   ```python
   # ❌ НЕПРАВИЛЬНО
   element = driver.find_element(By.ID, "search")

   # ✅ ПРАВИЛЬНО
   driver.get("https://example.com")
   time.sleep(2)
   element = driver.find_element(By.ID, "search")
   ```

### ✅ ЧТО ДЕЛАТЬ:

1. **Всегда начинать с `driver.get()`**
2. **Использовать debounce 500ms для ввода текста**
3. **Проверять ID и NAME в первую очередь**
4. **Объединять последовательные действия**
5. **Удалять избыточные клики и navigate**
6. **Тестировать на реальных сайтах**

---

## 📞 ПОДДЕРЖКА

Если что-то непонятно, обращайся к:
- **Полная спецификация:** `/home/user/auto2tesst/CHROME_EXTENSION_COMPLETE_SPEC.md`
- **Примеры плохого кода:** Там же, раздел "Примеры НЕПРАВИЛЬНОГО кода"
- **Примеры хорошего кода:** Там же, раздел "Примеры ПРАВИЛЬНОГО кода"

---

## 🚀 НАЧАЛО РАБОТЫ

1. **Прочитай полную спецификацию:**
   ```bash
   cat /home/user/auto2tesst/CHROME_EXTENSION_COMPLETE_SPEC.md
   ```

2. **Изучи текущий код Extension:**
   - `content/content.js` - event listener
   - `recorder/selector-generator.js` - selector generator
   - `generator/selenium-generator.js` - code generator

3. **Начни исправления с `content.js`** (debounce для объединения нажатий)

4. **Тестируй каждое изменение** на реальных сайтах

5. **Убедись что все 3 теста проходят** перед финальным коммитом

---

**УДАЧИ! 🎉**
