FROM python:2.7

# Install the UKWA Monitor package:
COPY . /monitor
RUN cd /monitor/ && pip install --no-cache-dir -r requirements.txt
RUN cd /monitor/ && python setup.py install

# And add the luigi configuration:
#ADD luigi.cfg /etc/luigi/luigi.cfg

# Run the dashboard
CMD ["gunicorn", "webapp.dashboard:app", "-b", "0.0.0.0:5000"]
