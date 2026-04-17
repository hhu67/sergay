#!/bin/bash

# Цвета для красоты
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===> Добавляем изменения...${NC}"
git add .

# Проверяем, передан ли коммит в аргументах
if [ -z "$1" ]
  then
    msg="Update $(date +'%Y-%m-%d %H:%M:%S')"
  else
    msg="$1"
fi

echo -e "${BLUE}===> Коммитим: ${GREEN}$msg${NC}"
git commit -m "$msg"

echo -e "${BLUE}===> Пушим на Gitek...${NC}"
git push gitek main

echo -e "${BLUE}===> Пушим на GitHub...${NC}"
git push github main

echo -e "${GREEN}Готово! Код обновлен в обоих репозиториях.${NC}"
