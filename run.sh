export MOZ_LOG=nsHttp:3
export MOZ_LOG_FILE=/dev/stdout
python3 src/main.py | grep ptracking > /tmp/bot.log