# Garret Motion - Technical round

This repository contains implementation of a calculation algorithm
which computes the costs of phone calls. The information about the
phone calls (phone number, call start time, call end time) are provided
in csv file. Settings about the rates and primetime can be configured
in a configuration file.

## Running the algorithm
Run the calculation with

```console
python src/main.py data/generated_sample_2.csv config/config.json
```

Results will be stored in newly created csv file 
`config/calculated_costs.csv`.

## Tests
Run the tests with

```console
python -m pytest tests/test.py
```

### Notes
Algorithm counts with phone calls during same day or over two consecutive days.
It's not currently designed to deal with longer phone calls (more than two days),
but this could be easily added.