FROM prom/prometheus:v2.34.0

COPY ./docker/prometheus.yml /etc/prometheus/prometheus.yml

# CMD [ "--config.file=/etc/prometheus/prometheus.yml", \
#       "--storage.tsdb.path=/prometheus", \
#       "--web.console.libraries=/usr/share/prometheus/console_libraries", \
#       "--web.console.templates=/usr/share/prometheus/consoles", \
#       "--query.lookback-delta=30s" ]
