FROM python:3.10-slim

WORKDIR /webui

COPY ./requirements.txt /webui/

RUN pip install --upgrade pip && pip install -r /webui/requirements.txt

EXPOSE 8501

COPY ./ /webui/

CMD ["streamlit", "run", "webui.py"]