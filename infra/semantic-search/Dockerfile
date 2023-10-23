
FROM python:3.8
COPY legal_radar /opt/legal_radar
COPY requirements.txt /opt
COPY .env /opt


WORKDIR /opt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PYTHONPATH "$PYTHONPATH:$(pwd)/legal_radar"
CMD streamlit run legal_radar/entrypoints/streamlit_app/app.py

EXPOSE 8501
