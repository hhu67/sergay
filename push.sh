#!/bin/bash

# =========================
# Настройки
# =========================
BRANCH="main"

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}===> Добавляем изменения...${NC}"
git add .

# =========================
# Коммит
# =========================
if [ -z "$1" ]; then
    msg="Update $(date +'%Y-%m-%d %H:%M:%S')"
else
    msg="$1"
fi

echo -e "${BLUE}===> Коммитим: ${GREEN}$msg${NC}"
git commit -m "$msg" 2>/dev/null || echo -e "${BLUE}Нет новых изменений${NC}"

# =========================
# Пуш на Gitek
# =========================
echo -e "${BLUE}===> Пушим на Gitek...${NC}"
if ! git push gitek "$BRANCH"; then
    echo -e "${RED}Ошибка при push в Gitek${NC}"
    exit 1
fi

# =========================
# Синхронизация с GitHub
# =========================
echo -e "${BLUE}===> Синхронизируемся с GitHub...${NC}"
if ! git pull github "$BRANCH" --rebase; then
    echo -e "${RED}Конфликт при pull!${NC}"
    echo -e "${RED}Реши конфликты вручную, затем выполни:${NC}"
    echo -e "${GREEN}git add . && git rebase --continue${NC}"
    exit 1
fi

# =========================
# Пуш на GitHub
# =========================
echo -e "${BLUE}===> Пушим на GitHub...${NC}"
if ! git push github "$BRANCH"; then
    echo -e "${RED}Ошибка при push в GitHub${NC}"
    exit 1
fi

# =========================
# Готово
# =========================
echo -e "${GREEN}✔ Готово! Код обновлен в обоих репозиториях.${NC}"
