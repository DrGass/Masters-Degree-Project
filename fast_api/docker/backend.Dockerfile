ARG         PYTHON_VER=3.12

FROM        --platform=linux/amd64 python:${PYTHON_VER} as fast-api-back

WORKDIR     /code

COPY        ./backend/requirements.txt /code/requirements.txt
RUN         pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY        ./backend/ /code

CMD         ["bash", "-c", "python app/run.py"]