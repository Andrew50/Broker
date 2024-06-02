#!/bin/sh

CONFIG_FILE="/models/models.config"
DEFAULT_CONFIG_FILE="/tmp/models.config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default models.config"
    cp $DEFAULT_CONFIG_FILE $CONFIG_FILE
fi

echo "Using models.config:"
cat $CONFIG_FILE

exec tensorflow_model_server \
  --port=8500 \
  --rest_api_port=8501 \
  --model_config_file=$CONFIG_FILE \
  --model_config_file_poll_wait_seconds=60
