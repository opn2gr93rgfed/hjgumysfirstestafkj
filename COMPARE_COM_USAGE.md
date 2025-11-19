# Compare.com Auto Insurance Quote Automation

## Overview

This example demonstrates how to use the **smart_no_api** provider to automate multi-step insurance quote forms with smart fallbacks and Octobrowser API integration.

## Files

- `example_compare_com_automation.py` - User code to paste into GUI editor
- `example_compare_com_data.csv` - Sample CSV data with test records

## CSV Data Format

| Field | Description | Example |
|-------|-------------|---------|
| Field 1 | ZIP Code | 33071 |
| Field 2 | Birth Month (MM) | 10 |
| Field 3 | Birth Day (DD) | 31 |
| Field 4 | Birth Year (YYYY) | 1963 |
| Field 5 | First Name | Janice |
| Field 6 | Last Name | North |
| Field 7 | Street Address | 1545 |
| Field 8 | Email Address | test@example.com |
| Field 9 | Phone Number | (714) 829-9472 |

## How to Use

### 1. Configure Octobrowser API

In the GUI **Octo API** tab:
- Enter your API Token (already configured: `aeffea9c9fcc40919aac1c9dc4eac5d0`)
- Configure profile settings (fingerprint, tags, etc.)

### 2. Configure Proxy (MANDATORY)

In the GUI **Proxies** tab:
- ✅ Enable proxy
- Select type (HTTP, SOCKS5, etc.)
- Enter host, port, login, password

**CRITICAL**: The smart_no_api provider requires proxy to be enabled.

### 3. Load CSV Data

In the GUI **Editor** tab:
- Click **"Загрузить CSV"**
- Select `example_compare_com_data.csv`
- CSV data will be embedded in the generated script

### 4. Load User Code

In the GUI **Editor** tab:
- Click **"Загрузить запись"**
- Select `example_compare_com_automation.py`
- The automation code will load into the editor

### 5. Select Provider

In the GUI **Editor** tab:
- Provider dropdown → Select **"smart_no_api"**

### 6. Generate Script

- Click **"Генерировать"**
- The complete script will be generated with:
  - Octobrowser API profile creation
  - Proxy injection
  - Smart helper functions
  - CSV data embedded
  - Your automation code wrapped

### 7. Run Script

- Click **"Запуск всех"**
- The script will:
  1. Create Octobrowser profile with proxy
  2. Start profile and get CDP endpoint
  3. Connect Playwright via CDP
  4. Run automation for each CSV row
  5. Clean up profiles after completion

## Smart Features

### Smart Click
```python
smart_click(page, [
    'role=button[name="See My Quotes"]',
    'button:has-text("See My Quotes")',
    'button:has-text("Get Quotes")'
], "See My Quotes Button")
```
- Tries multiple selectors in order
- Falls back if element not found
- Logs which selector worked

### Smart Fill
```python
smart_fill(page, [
    'role=textbox[name="Email address"]',
    'input[type="email"]',
    'input[placeholder*="email"]'
], data_row.get('Field 8', 'test@example.com'), "Email Address")
```
- Multiple selector fallbacks
- Uses CSV data dynamically
- Default values if CSV field missing

### Check Heading
```python
check_heading(page, ["Are you currently insured?", "Currently insured?"])
```
- Flexible heading detection
- Handles dynamic question ordering
- Validates page state

## Example Output

```
[MAIN] Запуск автоматизации через Octobrowser API...
[MAIN] API Token: aeffea9c9f...
[MAIN] ✓ ПРОКСИ ВКЛЮЧЕН: http://proxy.example.com:8080
[MAIN] Загружено 4 строк данных

############################################################
# ROW 1/4
############################################################
[PROFILE] Создание профиля: Auto Profile 1
[PROFILE] ⚠️ ПРОКСИ ОБЯЗАТЕЛЕН: http://proxy.example.com:8080
[PROFILE] API Response Status: 201
[PROFILE] ✓ Профиль создан: abc-123-def
[PROFILE] UUID: abc-123-def
[PROFILE] Запуск...
[PROFILE] ✓ Профиль запущен, CDP endpoint получен
[PROFILE] ✓ CDP endpoint получен

[ITERATION 1] Начало...
[SMART_FILL] Попытка 1/3: ZIP Code = 33071
[SMART_FILL] ✓ Заполнено: ZIP Code
[SMART_CLICK] Попытка 1/3: See My Quotes Button
[SMART_CLICK] ✓ Клик выполнен: See My Quotes Button
[CHECK_HEADING] ✓ Найден заголовок: Are you currently insured?
...
[SUCCESS] Quote flow completed for Janice
[ITERATION 1] ✓ Завершено успешно

[PROFILE] Остановка профиля
[PROFILE] ✓ Профиль остановлен
[MAIN] Пауза 3 секунды перед следующей итерацией...

############################################################
# ROW 2/4
############################################################
...
```

## Troubleshooting

### Profile Creation Fails
- **Check API token** - Verify token is correct in config.json
- **Check API limits** - Octobrowser has rate limits (50-200 RPM)
- **Check Octobrowser running** - Local API must be accessible at localhost:58888

### Proxy Issues
- **Enable proxy** - Must be enabled in GUI Proxies tab
- **Valid credentials** - Check proxy host, port, login, password
- **Test proxy** - Verify proxy works independently first

### Selector Not Found
- **Page changed** - Website layout may have changed
- **Add more fallbacks** - Add additional selectors to smart_click/smart_fill arrays
- **Increase timeout** - Some elements take longer to appear

### Data Issues
- **CSV encoding** - Use UTF-8 encoding
- **Field names** - Must be exactly "Field 1", "Field 2", etc.
- **Missing data** - Script has defaults if CSV field missing

## Advanced Usage

### Custom Proxy Per Row

Modify the profile creation to use different proxy for each iteration:

```python
# In CSV add: Field 10 = proxy_host, Field 11 = proxy_port
proxy_config['host'] = data_row.get('Field 10', 'default.proxy.com')
proxy_config['port'] = data_row.get('Field 11', '8080')
```

### Dynamic Fingerprints

Configure different OS/browser fingerprints per profile:

```python
profile_config['fingerprint'] = {
    "os": "mac",  # or "win", "lin"
    "browser": "chrome"
}
```

### Geolocation Spoofing

Match geolocation to ZIP code:

```python
profile_config['geolocation'] = {
    "latitude": 26.1224,
    "longitude": -80.1373,
    "accuracy": 100
}
```

## Notes

- **Legal Compliance**: This is for legitimate automation testing only
- **Rate Limiting**: Add delays between iterations to avoid detection
- **Data Privacy**: Never commit real user data to git
- **Proxy Required**: smart_no_api provider enforces proxy usage for anonymity

## Support

For issues with:
- **Octobrowser API** - https://docs.octobrowser.net/
- **Playwright** - https://playwright.dev/python/
- **Provider System** - Check `CLAUDE.md` in repository root
