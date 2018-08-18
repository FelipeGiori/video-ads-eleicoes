export MOZ_LOG=nsHttp:3
export MOZ_LOG_FILE=/dev/stdout | grep ptracking >> /tmp/bot.log 
python3 src/main.py
