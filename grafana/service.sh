cd src/ollamanet && make run && cd ../..
echo -e "\x1b[32m[+] Successfully launched ollamanet\x1b[0m"

cd src/top
nohup python top.py > log/top.log 2>&1 &
cd ../..

echo -e "\x1b[32m[+] Successfully launched top\x1b[0m"