sudo apt install tcpdump make 
pip install mysql-connector-python psutil GPUtil 
echo -e "\x1b[32m[+] Successfully installed required packages\x1b[0m"

cd compose && docker-compose up -d && cd ..
echo -e "\x1b[32m[+] Successfully launched docker containers gf-mysql and gf-grafana\x1b[0m"

echo -e "\x1b[32m[+] grafana is now available at http://127.0.0.1:3000 \x1b[0m"
echo -e "\x1b[32m[+] default username: admin, password: admin \x1b[0m"