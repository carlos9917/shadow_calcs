FROM python:3.9-slim

ARG PID
ARG GID
ARG CUSER

#set user Id and group Id
ENV PID=$PID
ENV GID=$GID
ENV CUSER=$CUSER

#RUN groupadd -g $GID $CUSER
#RUN useradd -u $PID -g $GID -d /home/$CUSER -m -s /bin/bash $CUSER && echo "$CUSER:$CUSER" | chpasswd && adduser $CUSER sudo
#

RUN pip install pipenv
#RUN chown -R $CUSER:grassuser /home/$CUSER/

WORKDIR /app
#WORKDIR /home/$CUSER/app

COPY ["Pipfile", "Pipfile.lock", "./"]
#COPY ["Pipfile", "./"]

#this one will install it in the system using the pipfile above
RUN pipenv install --system --deploy

#COPY ["main.py", "random_forest.bin", "./"]
COPY ["main.py", "./"]
COPY ["app", "./app"]
#COPY ["app", "/home/$USER/app"]
#expose the port 9696
EXPOSE 9696

ENTRYPOINT ["python", "main.py"]
#ENTRYPOINT ["uvicorn", "./main:app", "--host=0.0.0.0:8800","--reload"]
#ENTRYPOINT ["uvicorn", "app.app:app","--host=0.0.0.0:9696","--reload"]
