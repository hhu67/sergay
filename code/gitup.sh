#!/usr/bin/env bash

set -a
source .env
set +a

cd ~/sergay || exit 1

git add .

if ! git diff --cached --quiet; then
    git commit -m "update" || exit 1
else
    echo "Нет новых изменений"
fi

git pull --rebase "http://usergit.duckdns.org/igor/sergay.git" main || exit 1
git push "http://igor:${GIT}@usergit.duckdns.org/igor/sergay.git"
