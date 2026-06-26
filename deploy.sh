#!/usr/bin/env bash
#
# Деплой статического сайта в Yandex Object Storage (S3-совместимый API).
#
# Требуется один раз настроить профиль aws с ключами сервисного аккаунта:
#   aws configure --profile yandex
#     AWS Access Key ID     = <static key id сервисного аккаунта>
#     AWS Secret Access Key = <static key secret>
#     Default region        = ru-central1
#     Default output format  = json
#
# Запуск:
#   ./deploy.sh                 # деплой в бакет granopa.ru
#   BUCKET=other.ru ./deploy.sh # другой бакет
#
# Загружает только файлы сайта (index.html, styles.css, main.js, assets/).
# Сборочный артефакт таисия-сайт.html и доки НЕ загружаются.
set -euo pipefail
cd "$(dirname "$0")"

ENDPOINT="https://storage.yandexcloud.net"
BUCKET="${BUCKET:-granopa.ru}"
PROFILE="${AWS_PROFILE:-yandex}"
AWS=(aws --endpoint-url "$ENDPOINT" --profile "$PROFILE")

echo "→ Деплой в s3://$BUCKET (профиль: $PROFILE)"

# 1) HTML — короткий кэш, чтобы правки появлялись почти сразу
"${AWS[@]}" s3 cp index.html "s3://$BUCKET/index.html" \
  --content-type "text/html; charset=utf-8" \
  --cache-control "public, max-age=300"

# 2) CSS / JS — средний кэш
"${AWS[@]}" s3 cp styles.css "s3://$BUCKET/styles.css" \
  --content-type "text/css; charset=utf-8" \
  --cache-control "public, max-age=3600"
"${AWS[@]}" s3 cp main.js "s3://$BUCKET/main.js" \
  --content-type "application/javascript; charset=utf-8" \
  --cache-control "public, max-age=3600"

# 3) Картинки — длинный кэш, --delete убирает из бакета удалённые файлы
"${AWS[@]}" s3 sync assets "s3://$BUCKET/assets" \
  --cache-control "public, max-age=604800" \
  --delete

echo "✓ Загружено."
echo "  Если перед бакетом стоит Cloud CDN — сбрось кэш (purge),"
echo "  иначе старая версия будет отдаваться до истечения TTL."
