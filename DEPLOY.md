# Деплой — Yandex Object Storage + Cloud CDN + HTTPS

Статический сайт (`index.html` + `styles.css` + `main.js` + `assets/`) на
домене **granopa.ru** с HTTPS. Без сервера и без обслуживания.

## Архитектура

```
granopa.ru ──DNS──> Cloud CDN ──origin──> Object Storage (website endpoint)
                       │
                       └── TLS-сертификат из Certificate Manager (Let's Encrypt)
```

- **Object Storage** — хранит файлы, отдаёт `index.html` на `/` (website hosting).
- **Certificate Manager** — бесплатный Let's Encrypt сертификат, автопродление.
- **Cloud CDN** — отдаёт сайт по HTTPS на своём домене, кэширует, ускоряет.

Стоимость: копейки в месяц (хранение + трафик), несравнимо дешевле VM.

---

## Шаг 1. Домен

1. Купить **granopa.ru** на [reg.ru](https://reg.ru) (~200 ₽/год). Допуслуги не нужны.
2. **Рекомендуется:** делегировать DNS-зону в Yandex Cloud DNS — тогда проверка
   сертификата и записи для CDN (включая корневой домен) создаются автоматически,
   без ручной возни с apex-CNAME.
   - Yandex Cloud → **Cloud DNS** → создать **публичную зону** `granopa.ru.`
   - Скопировать выданные NS-серверы (`ns1.yandexcloud.net` и т.п.).
   - В reg.ru → «DNS-серверы» → прописать эти NS вместо reg.ru-овских.
   - Делегирование вступает в силу за 1–24 часа.

## Шаг 2. Бакет Object Storage

1. Yandex Cloud → **Object Storage** → **Создать бакет**.
   - **Имя**: `granopa.ru` (ровно как домен).
   - **Доступ**: «Публичный» на **чтение объектов** (нужно для отдачи сайта).
   - Класс хранилища: стандартный.
2. Открыть бакет → вкладка **«Веб-сайт»** (Website hosting) → включить:
   - **Главная страница**: `index.html`
   - **Страница ошибки**: `index.html` (одностраничник)
3. Запомнить **website endpoint**: `https://granopa.ru.website.yandexcloud.net`
   (именно website-эндпоинт, не объектный — он отдаёт index.html на `/`).

## Шаг 3. Ключ для загрузки + первый деплой

1. **Сервисный аккаунт**: IAM → создать `granopa-deployer` с ролью
   `storage.editor` на каталог (или на бакет).
2. **Статический ключ доступа**: у этого аккаунта → «Создать статический ключ».
   Сохранить **Key ID** и **Secret**.
3. Настроить локально:
   ```bash
   aws configure --profile yandex
   #   AWS Access Key ID     = <Key ID>
   #   AWS Secret Access Key = <Secret>
   #   Default region        = ru-central1
   #   output format         = json
   ```
4. Залить сайт:
   ```bash
   ./deploy.sh
   ```
   Проверить по website-эндпоинту (HTTP): открыть
   `https://granopa.ru.website.yandexcloud.net` — сайт должен открыться.

## Шаг 4. TLS-сертификат (Certificate Manager)

1. Yandex Cloud → **Certificate Manager** → **Создать** → «От Let's Encrypt».
2. Домены: `granopa.ru` и `www.granopa.ru`.
3. Тип проверки: **DNS**.
   - Если зона в Cloud DNS (Шаг 1) — нажать «Создать записи в Cloud DNS» (авто).
   - Если DNS в reg.ru — добавить выданные CNAME `_acme-challenge…` вручную.
4. Дождаться статуса **Issued** (обычно минуты).

## Шаг 5. Cloud CDN

1. Yandex Cloud → **Cloud CDN** → **Создать ресурс**.
   - **Источник (origin)**: тип «Своя строка/бакет» → website endpoint из Шага 2
     (`granopa.ru.website.yandexcloud.net`), протокол к источнику — HTTP.
   - **Личные домены**: `granopa.ru` и `www.granopa.ru`.
   - **Сертификат**: выбрать из Certificate Manager (Шаг 4).
   - **Редирект HTTP → HTTPS**: включить.
   - Кэш: можно оставить по заголовкам origin (мы их шлём из `deploy.sh`).
2. CDN выдаст **CNAME** (вида `cl-…edgecdn.ru`).

## Шаг 6. DNS — направить домен на CDN

- **Если зона в Cloud DNS:** в карточке CDN-ресурса нажать «Создать записи в
  Cloud DNS» — Yandex сам добавит записи для `granopa.ru` (корень) и `www`.
- **Если DNS в reg.ru:**
  - `www` → CNAME → `<CDN CNAME>` — без проблем.
  - корневой `granopa.ru` — CNAME на apex нельзя. Варианты:
    1. перенести зону в Cloud DNS (рекомендуется, см. Шаг 1), **или**
    2. в reg.ru настроить редирект `granopa.ru` → `https://www.granopa.ru`,
       а основным сделать `www`.

Проверка распространения:
```bash
dig +short granopa.ru
curl -I https://granopa.ru
```

## Шаг 7. Готово ✓

- Открыть `https://granopa.ru` — сайт по HTTPS.
- Проверить превью ссылки: вставить `https://granopa.ru` в Телеграм — должна
  показаться OG-картинка (`assets/og.jpg`).

---

## Обновление сайта дальше

```bash
# отредактировать index.html / styles.css / main.js / assets,
python3 build-single.py    # (опционально — самодостаточный файл для пересылки)
./deploy.sh                # залить в бакет
```
После деплоя — **сбросить кэш CDN**: Cloud CDN → ресурс → «Очистить кэш»
(можно «всё» или конкретные пути). Иначе старая версия отдаётся до истечения TTL.

## Заметки

- HTTPS на самом Object Storage нет — поэтому HTTPS даёт именно CDN. Прямой
  website-эндпоинт остаётся HTTP (для проверки), пользователи ходят через CDN.
- `index.html` отдаётся с коротким кэшом (5 мин), картинки — с длинным (неделя):
  правки текста видны быстро, тяжёлые ассеты не перекачиваются.
