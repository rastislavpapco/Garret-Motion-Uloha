# Garrett Motion - Technical round

This repository contains implementation of a calculation algorithm
which computes the costs of phone calls. The cost of a phone call is based on its
duration and also time of the day. The primetime during each day is set from
8:00 to 16:00. The cost of each started minute during primetime is 1 CZK.
The cost of each started minute outside primetime is 0.5 CZK. If the call
lasts longer than 5 minutes, then the cost of each new minute after that is
only 0.2 CZK. There is also a special promo event, where the most frequent
phone number gets to call for free.

The information about the phone calls (phone number, call start time, call end time)
are provided in csv file. Settings about the rates and primetime can be configured
in a configuration file.

## Running the algorithm
Run the calculation with

```console
python src/main.py data/generated_sample_2.csv config/config.json
```

Results will be stored in newly created csv file 
`data/calculated_costs.csv`.

## Tests
Run the tests with

```console
python -m pytest tests/test.py
```

### Notes
Algorithm counts with phone calls during same day or over two consecutive days.
It's not currently designed to deal with longer phone calls (more than two days),
but this could be easily added.