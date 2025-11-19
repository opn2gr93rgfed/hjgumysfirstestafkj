# ПОЛНОЕ ТЗ: Chrome Extension "Selenium Chrome Recorder" для auto2tesst

## 🎯 Цель проекта

Создать Chrome Extension который записывает действия пользователя на веб-странице и генерирует **чистый, валидный, надежный Python Selenium код** для вставки в приложение auto2tesst.

## 📋 Требования к генерируемому коду

### ✅ Код ДОЛЖЕН:

1. **Начинаться с перехода на страницу**
   ```python
   driver.get("https://example.com")
   time.sleep(2)
   ```

2. **Использовать ТОЛЬКО синтаксис `"{{переменная}}"` для параметризации**
   ```python
   element.send_keys("{{email}}")  # ✅ ПРАВИЛЬНО
   element.send_keys(email)        # ❌ НЕПРАВИЛЬНО
   ```

3. **НЕ содержать импортов** (auto2tesst добавит их сам)
   ```python
   # ❌ НЕ ДОБАВЛЯТЬ:
   # from selenium.webdriver.common.by import By
   # from selenium.webdriver.support.ui import WebDriverWait

   # ✅ ПРОСТО КОД ДЕЙСТВИЙ
   ```

4. **Объединять последовательные вводы в одно поле**
   ```python
   # ✅ ПРАВИЛЬНО (один send_keys):
   element.send_keys("{{username}}")

   # ❌ НЕПРАВИЛЬНО (несколько send_keys в одно поле):
   element.send_keys("J")
   element.send_keys("o")
   element.send_keys("h")
   element.send_keys("n")
   ```

5. **Использовать надежные селекторы в порядке приоритета:**
   - **Приоритет 1:** `By.ID` (если есть)
   - **Приоритет 2:** `By.NAME` (если есть)
   - **Приоритет 3:** `data-testid`, `data-test`, `data-qa`
   - **Приоритет 4:** `By.XPATH` с текстом (для кнопок/ссылок)
   - **Приоритет 5:** `By.CLASS_NAME` (простой класс)
   - **Последний шанс:** Простой CSS без `:nth-child()`

6. **НЕ записывать избыточные действия:**
   - ❌ Клик по input перед send_keys
   - ❌ Submit после клика по кнопке submit
   - ❌ Navigate после submit/click по ссылке
   - ❌ Повторные поиски одного элемента

---

## 🏗️ Архитектура решения

```
Chrome Extension
│
├── content.js          - Запись действий на странице
├── background.js       - Хранение записанных действий
├── popup.js            - UI и управление
├── popup.html          - Интерфейс
│
└── Modules:
    ├── recorder/
    │   ├── event-listener.js      - Слушатели событий DOM
    │   └── selector-generator.js  - Генерация селекторов
    │
    └── generator/
        ├── action-optimizer.js    - Оптимизация действий
        └── selenium-generator.js  - Генерация Python кода
```

---

## 📝 Детальная спецификация модулей

### 1. EVENT LISTENER (event-listener.js)

**Задача:** Записывать действия пользователя на странице.

**Что записывать:**

| Событие | Когда записывать | Данные для записи |
|---------|------------------|-------------------|
| **navigate** | При начале записи | `url`, `timestamp` |
| **click** | На BUTTON, A, элементах с `onclick` | `element`, `selector`, `url` |
| **type** | На INPUT, TEXTAREA при вводе текста | `element`, `selector`, `value`, `url` |
| **change** | На SELECT при изменении | `element`, `selector`, `value`, `url` |
| **submit** | На FORM при отправке | `element`, `selector`, `url` |

**Что НЕ записывать:**
- ❌ Клики по обычным DIV, SPAN (если нет `onclick`)
- ❌ Движения мыши (mousemove, mouseover)
- ❌ Скроллы (scroll)
- ❌ Focus/blur на input (записываем только ввод текста)

**Алгоритм записи navigate:**

```javascript
// При начале записи - ОБЯЗАТЕЛЬНО записать текущий URL
function startRecording() {
    const initialAction = {
        type: 'navigate',
        url: window.location.href,
        timestamp: Date.now()
    };

    recordedActions.push(initialAction);
    isRecording = true;

    console.log('Recording started with initial URL:', initialAction.url);
}
```

**Алгоритм записи type (ввод текста):**

```javascript
// Используем debounce для объединения быстрых вводов
let typeTimeout = null;
let currentTypeElement = null;
let currentTypeValue = '';

function handleKeyup(event) {
    if (!isRecording) return;

    const element = event.target;
    if (!['INPUT', 'TEXTAREA'].includes(element.tagName)) return;

    // Если это тот же элемент - накапливаем значение
    if (currentTypeElement === element) {
        currentTypeValue = element.value;
    } else {
        // Новый элемент - сохраняем предыдущий (если был)
        if (currentTypeElement) {
            saveTypeAction(currentTypeElement, currentTypeValue);
        }
        currentTypeElement = element;
        currentTypeValue = element.value;
    }

    // Сбрасываем таймер
    clearTimeout(typeTimeout);

    // Ждем 500мс после последнего нажатия
    typeTimeout = setTimeout(() => {
        if (currentTypeElement) {
            saveTypeAction(currentTypeElement, currentTypeValue);
            currentTypeElement = null;
            currentTypeValue = '';
        }
    }, 500);
}

function saveTypeAction(element, value) {
    if (!value) return; // Не записываем пустые значения

    const action = {
        type: 'type',
        element: {
            tagName: element.tagName,
            id: element.id,
            name: element.name,
            type: element.type
        },
        value: value,
        url: window.location.href,
        timestamp: Date.now()
    };

    // Генерируем селектор
    action.selector = selectorGenerator.generate(element);

    recordedActions.push(action);
    console.log('Recorded type action:', action);
}
```

---

### 2. SELECTOR GENERATOR (selector-generator.js)

**Задача:** Генерировать НАДЕЖНЫЕ селекторы для элементов.

**КРИТИЧЕСКИ ВАЖНО:** Никогда не использовать хрупкие селекторы!

**Алгоритм генерации селектора:**

```javascript
class SelectorGenerator {
    generate(element) {
        // Приоритет 1: ID (самый надежный)
        if (element.id && this.isUniqueById(element.id)) {
            return {
                type: 'id',
                value: element.id
            };
        }

        // Приоритет 2: NAME
        if (element.name && this.isUniqueByName(element.name)) {
            return {
                type: 'name',
                value: element.name
            };
        }

        // Приоритет 3: data-test* атрибуты
        const testAttr = this.findTestAttribute(element);
        if (testAttr) {
            return {
                type: 'css',
                value: `[${testAttr.name}="${testAttr.value}"]`
            };
        }

        // Приоритет 4: XPath с текстом (для кнопок/ссылок)
        if (['BUTTON', 'A'].includes(element.tagName)) {
            const text = this.getCleanText(element);
            if (text && text.length <= 30) {
                return {
                    type: 'xpath',
                    value: `//${element.tagName.toLowerCase()}[contains(text(), "${text}")]`
                };
            }
        }

        // Приоритет 5: Уникальный класс
        const uniqueClass = this.findUniqueClass(element);
        if (uniqueClass) {
            return {
                type: 'class',
                value: uniqueClass
            };
        }

        // Последний шанс: простой CSS
        return {
            type: 'css',
            value: this.buildSimpleCss(element)
        };
    }

    isUniqueById(id) {
        return document.querySelectorAll(`#${id}`).length === 1;
    }

    isUniqueByName(name) {
        return document.querySelectorAll(`[name="${name}"]`).length === 1;
    }

    findTestAttribute(element) {
        const testAttrs = ['data-testid', 'data-test', 'data-qa', 'data-cy'];
        for (const attr of testAttrs) {
            const value = element.getAttribute(attr);
            if (value) {
                return { name: attr, value: value };
            }
        }
        return null;
    }

    getCleanText(element) {
        let text = element.textContent || element.innerText || '';
        text = text.trim();
        text = text.substring(0, 30); // Максимум 30 символов
        text = text.replace(/\s+/g, ' '); // Множественные пробелы → один
        text = text.replace(/\n/g, ''); // Убираем переносы
        return text;
    }

    findUniqueClass(element) {
        const classes = Array.from(element.classList)
            .filter(cls => {
                // Исключаем служебные классы
                if (cls.match(/active|hover|focus|disabled|selected/)) return false;
                // Исключаем классы с цифрами (могут меняться)
                if (cls.match(/\d+$/)) return false;
                return true;
            });

        for (const cls of classes) {
            if (document.querySelectorAll(`.${cls}`).length === 1) {
                return cls;
            }
        }

        return null;
    }

    buildSimpleCss(element) {
        // Простой CSS БЕЗ :nth-child()
        let selector = element.tagName.toLowerCase();

        // Добавляем первый значимый класс
        const classes = Array.from(element.classList)
            .filter(cls => !cls.match(/active|hover|focus|disabled/));

        if (classes[0]) {
            selector += `.${classes[0]}`;
        }

        return selector;
    }
}
```

**ЗАПРЕЩЕНО использовать:**
```javascript
// ❌ НИКОГДА НЕ ИСПОЛЬЗОВАТЬ:
":nth-child(2)"
":nth-of-type(3)"
"div > div > div > span > a"  // длинные цепочки
"/html/body/div[1]/div[2]/..."  // абсолютные XPath
```

---

### 3. ACTION OPTIMIZER (action-optimizer.js)

**Задача:** Оптимизировать записанные действия перед генерацией кода.

**Оптимизации:**

#### 3.1. Объединение последовательных send_keys

```javascript
class ActionOptimizer {
    optimizeTypeActions(actions) {
        const optimized = [];
        let i = 0;

        while (i < actions.length) {
            const action = actions[i];

            if (action.type === 'type') {
                // Собираем ВСЕ последовательные вводы в одно поле
                let combinedValue = action.value;
                let j = i + 1;

                while (j < actions.length &&
                       actions[j].type === 'type' &&
                       this.isSameSelector(actions[j].selector, action.selector)) {
                    combinedValue = actions[j].value; // Берем ПОСЛЕДНЕЕ значение!
                    j++;
                }

                // Создаем ОДНО действие с финальным значением
                optimized.push({
                    ...action,
                    value: combinedValue
                });

                i = j; // Пропускаем обработанные
            } else {
                optimized.push(action);
                i++;
            }
        }

        return optimized;
    }

    isSameSelector(sel1, sel2) {
        return sel1.type === sel2.type && sel1.value === sel2.value;
    }
}
```

#### 3.2. Удаление кликов перед send_keys

```javascript
removeClicksBeforeType(actions) {
    const optimized = [];

    for (let i = 0; i < actions.length; i++) {
        const action = actions[i];

        // Если это клик по input
        if (action.type === 'click' &&
            action.element?.tagName === 'INPUT' &&
            i + 1 < actions.length) {

            const nextAction = actions[i + 1];

            // И следующее действие - ввод в то же поле
            if (nextAction.type === 'type' &&
                this.isSameSelector(nextAction.selector, action.selector)) {
                // Пропускаем клик - send_keys сам активирует поле
                continue;
            }
        }

        optimized.push(action);
    }

    return optimized;
}
```

#### 3.3. Удаление navigate после submit/click

```javascript
removeRedundantNavigates(actions) {
    const optimized = [];

    for (let i = 0; i < actions.length; i++) {
        const action = actions[i];

        // Если это navigate
        if (action.type === 'navigate' && i > 0) {
            const prevAction = optimized[optimized.length - 1];

            // Пропускаем navigate после:
            if (prevAction.type === 'submit') {
                console.log('Skipping navigate after submit');
                continue;
            }

            if (prevAction.type === 'click' &&
                ['BUTTON', 'A'].includes(prevAction.element?.tagName)) {
                console.log('Skipping navigate after button/link click');
                continue;
            }
        }

        optimized.push(action);
    }

    return optimized;
}
```

#### 3.4. Полная оптимизация

```javascript
optimize(actions) {
    console.log('Original actions:', actions.length);

    let optimized = actions;

    // Шаг 1: Объединяем последовательные вводы
    optimized = this.optimizeTypeActions(optimized);
    console.log('After type optimization:', optimized.length);

    // Шаг 2: Убираем клики перед вводом
    optimized = this.removeClicksBeforeType(optimized);
    console.log('After click optimization:', optimized.length);

    // Шаг 3: Убираем избыточные navigate
    optimized = this.removeRedundantNavigates(optimized);
    console.log('After navigate optimization:', optimized.length);

    return optimized;
}
```

---

### 4. SELENIUM GENERATOR (selenium-generator.js)

**Задача:** Генерировать Python Selenium код для auto2tesst.

**КРИТИЧЕСКИ ВАЖНО:**
- ❌ **НЕ ДОБАВЛЯТЬ** импорты
- ✅ Использовать синтаксис `"{{переменная}}"`
- ✅ Начинать с `driver.get()`
- ✅ Использовать `WebDriverWait`

```javascript
class SeleniumGenerator {
    constructor(options = {}) {
        this.options = {
            useParameters: options.useParameters || false,
            addComments: options.addComments !== false, // По умолчанию true
            addWaits: options.addWaits !== false,       // По умолчанию true
            ...options
        };
        this.optimizer = new ActionOptimizer();
    }

    generateForAuto2tesst(actions) {
        if (!actions || actions.length === 0) {
            return '# Нет записанных действий\npass';
        }

        // === ОПТИМИЗАЦИЯ ===
        const optimized = this.optimizer.optimize(actions);
        console.log(`Optimized: ${actions.length} → ${optimized.length} actions`);

        const code = [];

        // === ЗАГОЛОВОК ===
        code.push('# Автоматически сгенерировано: Selenium Chrome Recorder');
        code.push(`# Дата: ${new Date().toLocaleString('ru-RU')}`);
        code.push(`# Действий: ${optimized.length}`);
        code.push('');

        // === ПАРАМЕТРИЗАЦИЯ ===
        if (this.options.useParameters) {
            const variables = this.findVariables(optimized);
            if (variables.length > 0) {
                code.push('# 💡 Найденные переменные для параметризации:');
                variables.forEach(v => code.push(`#    {{${v}}}`));
                code.push('# Используйте их в auto2tesst для мультизапуска с CSV');
                code.push('');
            }
        }

        // === ГЕНЕРАЦИЯ ДЕЙСТВИЙ ===
        for (let i = 0; i < optimized.length; i++) {
            const action = optimized[i];

            // Комментарий
            if (this.options.addComments) {
                const desc = this.getActionDescription(action);
                code.push(`# ${i + 1}. ${desc}`);
            }

            // Код действия
            const actionCode = this.generateAction(action);
            code.push(actionCode);

            // Пауза
            if (this.options.addWaits && i < optimized.length - 1) {
                code.push('time.sleep(0.5)');
            }

            code.push('');
        }

        return code.join('\n');
    }

    findVariables(actions) {
        const variables = new Set();

        actions.forEach((action, index) => {
            if (action.type === 'type' && action.value) {
                const varName = this.createVariableName(action, index);
                variables.add(varName);
            }
        });

        return Array.from(variables);
    }

    createVariableName(action, index) {
        // Используем ID или name элемента
        if (action.element?.id) {
            return action.element.id;
        }
        if (action.element?.name) {
            return action.element.name;
        }
        // Иначе - generic имя
        return `field_${index + 1}`;
    }

    getActionDescription(action) {
        let desc = '';

        switch (action.type) {
            case 'navigate':
                desc = `Переход на ${action.url}`;
                break;

            case 'click':
                const elementName = action.element?.id ||
                                  action.element?.name ||
                                  action.element?.tagName || 'элемент';
                // Ограничиваем длину описания
                desc = `Клик по ${elementName}`.substring(0, 50);
                break;

            case 'type':
                const fieldName = action.element?.id ||
                                action.element?.name || 'поле';
                desc = `Ввод текста в ${fieldName}`.substring(0, 50);
                break;

            case 'change':
                desc = 'Изменение значения select';
                break;

            case 'submit':
                desc = 'Отправка формы';
                break;

            default:
                desc = action.type;
        }

        // Убираем переносы строк
        desc = desc.replace(/\n/g, ' ').replace(/\s+/g, ' ');

        return desc;
    }

    generateAction(action) {
        switch (action.type) {
            case 'navigate':
                return this.generateNavigate(action);
            case 'click':
                return this.generateClick(action);
            case 'type':
                return this.generateType(action);
            case 'change':
                return this.generateChange(action);
            case 'submit':
                return this.generateSubmit(action);
            default:
                return `# Неизвестное действие: ${action.type}`;
        }
    }

    generateNavigate(action) {
        return `driver.get("${action.url}")\ntime.sleep(2)`;
    }

    generateClick(action) {
        const selector = this.formatSelector(action.selector);
        return `element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(${selector})
)
element.click()`;
    }

    generateType(action) {
        const selector = this.formatSelector(action.selector);

        let value;
        if (this.options.useParameters) {
            const varName = this.createVariableName(action, 0);
            // ВАЖНО: Для auto2tesst используем "{{variable}}" в КАВЫЧКАХ!
            value = `"{{${varName}}}"`;
        } else {
            value = `"${this.escapeString(action.value)}"`;
        }

        return `element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(${selector})
)
element.send_keys(${value})`;
    }

    generateChange(action) {
        const selector = this.formatSelector(action.selector);
        const value = this.escapeString(action.value);

        return `element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(${selector})
)
select = Select(element)
select.select_by_visible_text("${value}")`;
    }

    generateSubmit(action) {
        const selector = this.formatSelector(action.selector);

        return `element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(${selector})
)
element.submit()`;
    }

    formatSelector(selector) {
        switch (selector.type) {
            case 'id':
                return `(By.ID, "${selector.value}")`;
            case 'name':
                return `(By.NAME, "${selector.value}")`;
            case 'class':
                return `(By.CLASS_NAME, "${selector.value}")`;
            case 'css':
                return `(By.CSS_SELECTOR, "${this.escapeString(selector.value)}")`;
            case 'xpath':
                return `(By.XPATH, "${this.escapeString(selector.value)}")`;
            default:
                return `(By.CSS_SELECTOR, "body")`;
        }
    }

    escapeString(str) {
        return str.replace(/\\/g, '\\\\')
                  .replace(/"/g, '\\"')
                  .replace(/\n/g, '\\n');
    }
}
```

---

## 📊 Примеры ПРАВИЛЬНОЙ генерации

### Пример 1: Простой поиск на Wikipedia

**Действия пользователя:**
1. Открыл wikipedia.org
2. Кликнул в поле поиска
3. Ввел "Python"
4. Кликнул кнопку Search

**ПРАВИЛЬНЫЙ результат:**

```python
# Автоматически сгенерировано: Selenium Chrome Recorder
# Дата: 16.11.2025, 23:00:00
# Действий: 3

# 1. Переход на https://www.wikipedia.org/
driver.get("https://www.wikipedia.org/")
time.sleep(2)

# 2. Ввод текста в searchInput
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "searchInput"))
)
element.send_keys("Python")
time.sleep(0.5)

# 3. Клик по Search
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
)
element.click()
```

### Пример 2: Форма регистрации с параметризацией

**Действия пользователя:**
1. Открыл форму
2. Ввел имя
3. Ввел email
4. Кликнул Submit

**ПРАВИЛЬНЫЙ результат (с параметризацией):**

```python
# Автоматически сгенерировано: Selenium Chrome Recorder
# Дата: 16.11.2025, 23:00:00
# Действий: 4

# 💡 Найденные переменные для параметризации:
#    {{firstName}}
#    {{email}}
# Используйте их в auto2tesst для мультизапуска с CSV

# 1. Переход на https://example.com/register
driver.get("https://example.com/register")
time.sleep(2)

# 2. Ввод текста в firstName
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "firstName"))
)
element.send_keys("{{firstName}}")
time.sleep(0.5)

# 3. Ввод текста в email
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)
element.send_keys("{{email}}")
time.sleep(0.5)

# 4. Клик по Submit
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
)
element.click()
```

---

## ❌ Примеры НЕПРАВИЛЬНОЙ генерации

### Плохой пример 1: Нет driver.get()

```python
# ❌ НЕПРАВИЛЬНО - код начинается с клика, а не с перехода!
# 1. Клик по элементу
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "searchInput"))
)
element.click()
```

### Плохой пример 2: Дублирование send_keys

```python
# ❌ НЕПРАВИЛЬНО - несколько send_keys в одно поле!
element.send_keys("J")
element.send_keys("o")
element.send_keys("h")
element.send_keys("n")

# ✅ ПРАВИЛЬНО - один send_keys:
element.send_keys("John")
```

### Плохой пример 3: Переменные без кавычек

```python
# ❌ НЕПРАВИЛЬНО - переменная без кавычек!
element.send_keys(username)

# ✅ ПРАВИЛЬНО - с кавычками и {{}}:
element.send_keys("{{username}}")
```

### Плохой пример 4: Плохие селекторы

```python
# ❌ НЕПРАВИЛЬНО - хрупкие селекторы!
By.CSS_SELECTOR, "div > div > div > span:nth-child(2)"
By.XPATH, "/html/body/div[1]/div[2]/..."

# ✅ ПРАВИЛЬНО - надежные селекторы:
By.ID, "username"
By.NAME, "email"
By.XPATH, "//button[contains(text(), 'Submit')]"
```

### Плохой пример 5: Избыточные navigate

```python
# ❌ НЕПРАВИЛЬНО - navigate после клика по кнопке!
element.click()
driver.get("https://example.com/next-page")  # <- ДУБЛЬ!

# ✅ ПРАВИЛЬНО - только клик:
element.click()
```

---

## 🧪 Тестирование

### Тест 1: Wikipedia поиск

1. Открыть https://www.wikipedia.org/
2. Начать запись
3. Кликнуть в поле поиска
4. Ввести "Selenium"
5. Кликнуть Search
6. Остановить запись
7. Generate for auto2tesst

**Ожидаемый результат: 3 действия**
```python
driver.get("https://www.wikipedia.org/")
element.send_keys("Selenium")
element.click()
```

### Тест 2: Форма с параметризацией

1. Открыть форму регистрации
2. Начать запись
3. Ввести имя "John"
4. Ввести email "john@example.com"
5. Кликнуть Submit
6. Остановить запись
7. Включить параметризацию
8. Generate for auto2tesst

**Ожидаемый результат: 4 действия с {{переменными}}**
```python
driver.get("https://...")
element.send_keys("{{firstName}}")
element.send_keys("{{email}}")
element.click()
```

### Тест 3: Быстрый ввод (объединение)

1. Открыть форму
2. Начать запись
3. Быстро ввести "John" (по одной букве)
4. Остановить запись
5. Generate for auto2tesst

**Ожидаемый результат: 2 действия (НЕ 5!)**
```python
driver.get("https://...")
element.send_keys("John")  # <- ОДНО действие, не четыре!
```

---

## ✅ Критерии приемки

Плагин считается **ГОТОВЫМ**, если:

1. ✅ Код ВСЕГДА начинается с `driver.get(url)`
2. ✅ НЕТ импортов в сгенерированном коде
3. ✅ Параметризация использует `"{{variable}}"` с кавычками
4. ✅ Последовательные send_keys объединены в один
5. ✅ НЕТ кликов перед send_keys
6. ✅ НЕТ navigate после submit/click
7. ✅ Используются ID/NAME селекторы (если есть)
8. ✅ НЕТ `:nth-child()` в обычных случаях
9. ✅ НЕТ абсолютных XPath
10. ✅ Код валидируется через `compile()` без ошибок
11. ✅ Код работает в auto2tesst без исправлений
12. ✅ Переменные из параметризации работают с CSV

---

## 📦 Пример финальной структуры файлов

```
chrome-extension/
├── manifest.json
├── popup.html
├── popup.js
├── content.js
├── background.js
│
├── recorder/
│   ├── event-listener.js       - Запись событий
│   └── selector-generator.js   - Генерация селекторов
│
└── generator/
    ├── action-optimizer.js     - Оптимизация действий
    └── selenium-generator.js   - Генерация Python кода
```

---

## 🚀 Итоговый чеклист разработки

### Этап 1: Запись действий
- [ ] Записывается начальный navigate при старте
- [ ] Записываются click на кнопках/ссылках
- [ ] Записываются type с debounce (500мс)
- [ ] НЕ записываются лишние события (hover, scroll, focus)

### Этап 2: Генерация селекторов
- [ ] Приоритет: ID > NAME > data-test* > XPath > CLASS > CSS
- [ ] НЕТ `:nth-child()` без необходимости
- [ ] НЕТ абсолютных XPath
- [ ] Текст в XPath ≤ 30 символов

### Этап 3: Оптимизация
- [ ] Объединены последовательные send_keys
- [ ] Удалены клики перед send_keys
- [ ] Удалены navigate после submit/click
- [ ] Логи показывают сколько действий было → стало

### Этап 4: Генерация кода
- [ ] НЕТ импортов
- [ ] Есть driver.get() в начале
- [ ] Параметризация: `"{{variable}}"`
- [ ] Используется WebDriverWait
- [ ] Комментарии ≤ 50 символов

### Этап 5: Тестирование
- [ ] Протестирован на 5+ разных сайтах
- [ ] Код вставлен в auto2tesst без ошибок
- [ ] Валидация через `compile()` проходит
- [ ] Параметризация работает с CSV
- [ ] Мультизапуск работает корректно

---

## 🎯 Финальная проверка

Перед релизом **ОБЯЗАТЕЛЬНО** проверить на этих 3 тестах:

**Тест A: Wikipedia**
- Действий записано: ~5-7
- Действий после оптимизации: 3
- Код валиден: ✅
- Запускается в auto2tesst: ✅

**Тест B: Форма регистрации**
- Действий записано: ~10-15
- Действий после оптимизации: 4-5
- Параметризация работает: ✅
- CSV мультизапуск работает: ✅

**Тест C: Сложный сценарий (несколько форм)**
- Действий записано: ~20-30
- Действий после оптимизации: 8-12
- Все селекторы надежные: ✅
- Нет дублей navigate: ✅

---

**Если ВСЕ критерии выполнены - плагин готов! 🎉**

**Если хотя бы один НЕ выполнен - продолжить доработку!**
