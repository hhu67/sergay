set -a
source .env
set +a

cd ~/sergay || exit 1
git rebase --continue 

git add .

if ! git diff --cached --quiet; then
    git commit -m "update" || exit 1
else
    echo "Нет новых изменений"
fi

git pull --rebase "http://usergit.duckdns.org:3000/igor/sergay.git" main || exit 1
git push "http://igor:${GIT}@usergit.duckdns.org:3000/igor/sergay.git"
cp /root/sergay/code/sergay.json /root/api/sergay.json 
