FROM python:3.8.7

# copy and install requirements
# running this beforehand avoids invalidating cache for this step when code changes
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
# uwsgi not included in requirements because problems installing on windows
RUN pip3 install uwsgi

# copy code to container
COPY . /

# set working directory inside the container
WORKDIR /src 

# overwrite with "python app.py dev" if you want to run the app with uwsgi
CMD ["uwsgi", "app.ini"]
# CMD ["uwsgi", "--socket", "0.0.0.0:8080", "--protocol=http", "-w", "app:app"]
# CMD ["python", "app.py", "dev"]