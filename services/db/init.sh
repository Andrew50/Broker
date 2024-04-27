#!/bin/bash

# Function to load data
load_data() {
    sleep 20  # Delay to ensure PostgreSQL is ready

    total_files=$(ls -1 /postgres-data/quotes/*.csv | wc -l)
    current_file=0

    for file in /postgres-data/quotes/*.csv; do
        current_file=$((current_file+1))
        echo "Processing file $current_file of $total_files: $file"
        psql -U postgres -c \
        "\\COPY quotes_1_extended(ticker_id, extended_hours, t, open, high, low, close, volume) FROM '${file}' WITH (FORMAT csv, HEADER false)"
    done

    # Add constraints after all files are processed
    psql -U postgres -c "ALTER TABLE quotes_1_extended ADD PRIMARY KEY (ticker_id, t);"
    psql -U postgres -c "ALTER TABLE quotes_1_extended ADD FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id) ON DELETE CASCADE;"
}

# Run the load data function in the background
load_data &

