cd compose
docker-compose stop
echo -e "\x1b[32m[+]Successfully stopped docker containers gf-mysql and gf-grafana\x1b[0m"

PROCESS_NAME="tailf.py"
PIDS=$(ps aux | grep $PROCESS_NAME | grep -v grep | awk '{print $2}')

# 检查是否找到了进程
if [ -z "$PIDS" ]; then
  echo "Unable to find $PROCESS_NAME"
fi

# 杀死找到的进程
for PID in $PIDS; do
  sudo kill $PID
  echo "Killed process $PID#$PROCESS_NAME"
done

PROCESS_NAME="listen.sh"
PIDS=$(ps aux | grep $PROCESS_NAME | grep -v grep | awk '{print $2}')

# 检查是否找到了进程
if [ -z "$PIDS" ]; then
  echo "Unable to find $PROCESS_NAME"
fi

# 杀死找到的进程
for PID in $PIDS; do
  sudo kill $PID
  echo "Killed process $PID#$PROCESS_NAME"
done

PROCESS_NAME="top.py"
PIDS=$(ps aux | grep $PROCESS_NAME | grep -v grep | awk '{print $2}')

# 检查是否找到了进程
if [ -z "$PIDS" ]; then
  echo "Unable to find $PROCESS_NAME"
fi

# 杀死找到的进程
for PID in $PIDS; do
  sudo kill $PID
  echo "Killed process $PID#$PROCESS_NAME"
done