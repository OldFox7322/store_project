#!/bin/bash

echo "Launching the automatic script"
echo '-----------------------------------'




echo "1 Launching Docker Desctop "

systemctl --user start docker-desktop
echo "Waiting 20 seconds for fully launching"
sleep 20
pgrep -f "Docker Desktop" > /dev/null
if [ $? -ne 0 ]; then
	echo "Docker Desktop is not running"
	exit 1 
fi



echo "2 Launching Docker-Compose"

docker-compose up -d
if [ $? -ne 0 ]; then
	echo "Error docker-compose is not running"
	exit 1
fi

echo "Waiting 10 seconds for fully launching"
sleep 10



echo "3 Activation virtual environment"

source venv/bin/activate
if [ -z "$VIRTUAL_ENV" ]; then
	echo "Error: virtual environment not active"
	exit 1
fi



echo "4 Installing dependencies "

pip install -r requirements.txt



echo "5 Application of Alembic migrations"

alembic upgrade head
if [ $? -ne 0 ]; then
	echo "Erorr: Migration not applied"
	docker-compose down
	exit 1
fi


echo "6 Launch the tests"

pytest
if [ $? -ne 0 ]; then
	echo "Erorr: The tests failed"
	docker-compose down
	exit 1
fi


echo "7 Runnind the Uvicorn application in the background"

uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
sleep 5 


echo "8 Open the app in browser"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  xdg-open http://127.0.0.1:8000/docs
elif [[ "$OSTYPE" == "darwin"* ]]; then
  open http://127.0.0.1:8000/docs
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  start http://127.0.0.1:8000/docs
else
  echo "Unable to determine operating system. Open http://127.0.0.1:8000/docs вручну."
fi


echo '--------------------------------'
echo 'The script is comlete. Press Ctrl+C to stop the application and Docker-Compose'


trap "echo 'Stop the application...'; kill \$! ; docker-compose down ; exit 0" INT
wait