###yum install mail postfix
###vi /etc/mail.rc
###set from=psinfomail@163.com smtp=smtp.163.com
###set smtp-auth-user=邮箱用户名 smtp-auth-password=邮箱密码 smtp-auth=login

flist=$(cat pids.txt)
for fn in $flist
do
	pid=$(cat $fn)
	v=$(ps ax | awk '{print $1}' | grep $pid)
	if [ ! -n "$v" ]; then
		echo $fn "is not runing"
        echo $fn "is not runing" | mail -s "Alert: server stop $fn" leuting@qq.com
	else
		echo $fn "is runing"
	fi
done 
