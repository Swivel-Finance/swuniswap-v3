FROM python:3.7

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Run the application:
COPY helpers ./helpers
COPY orders ./orders
COPY constants ./constants
COPY swuniswap-v3.py .
COPY swuniswap-v3-zcTokens.py .

ENV INTERACTIVE=F

CMD ["python3", "swuniswap-v3.py"]