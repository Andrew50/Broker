FROM tensorflow/serving
COPY models.config /tmp/models.config
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
ADD default /models/default/1
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN mkdir -p /models && chmod -R 777 /models
#ENV MODEL_BASE_PATH=/models
#ENV MODEL_CONFIG_FILE=/models/models.config
RUN ls -l /models
EXPOSE 8500
EXPOSE 8501
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
