pagemonitor

simple, stable and efficient page monitor by python

json-config format: url list
url, status(0/1, default 0), interval(by second, default 180), failed times(to alert, default 3), alert interval(by second, default 600), re list


work flow:
1. load config
2. do 3 to 5 in loop
3. download each page
4. check by re list
5. send alert letters

