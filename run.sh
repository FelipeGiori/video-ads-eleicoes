export MOZ_LOG=timestamp,nsHttp:3
export MOZ_LOG_FILE=/dev/stdout | grep ptracking 
cd src/
python3 main.py
