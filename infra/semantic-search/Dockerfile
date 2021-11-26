
FROM python:3.8
ADD legal_radar /opt/legal_radar
COPY requirements-semantic-search.txt /opt
COPY .env /opt


WORKDIR /opt
RUN pip install --upgrade pip
RUN pip install -r requirements-semantic-search.txt
RUN python -m spacy download en_core_web_sm
ENV PYTHONPATH "$PYTHONPATH:$(pwd)/legal_radar"
CMD streamlit run legal_radar/entrypoints/streamlit_app/app.py
