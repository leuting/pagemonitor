###yum update nss

PID_FILE=pm.pid
CNF_FILE=conf.json
nohup python pm.py -c $CNF_FILE >>std.log 2>>err.log &
echo $! > $PID_FILE 
