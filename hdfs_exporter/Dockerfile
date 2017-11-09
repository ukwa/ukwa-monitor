FROM python:2.7

# Install the Monitor package:
COPY . /monitor
RUN cd /monitor/ && pip install --no-cache-dir -r requirements.txt
RUN cd /monitor/ && python setup.py install

# Run the dashboard
CMD ["gunicorn", "webapp:app", "-b", "0.0.0.0:5000"]
