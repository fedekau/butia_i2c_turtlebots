#
# Regular cron jobs for the turtlebots package
#
0 4	* * *	root	[ -x /usr/bin/turtlebots_maintenance ] && /usr/bin/turtlebots_maintenance
