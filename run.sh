export MOZ_LOG=timestamp,nsHttp:3
export MOZ_LOG_FILE=/dev/stdout | grep ptracking 
python3 src/main.py