Requirements
============

```
$ python3 -m venv venv
```


LDL VM Monitoring Pusher
========================

We've always had difficulties tracking the status of DLS LDL VMs, especially their network connectivity.

Each LDL VM has a root cronjob that curls "http://ld02:8983/wa/monitor?host=$(hostname -f)" (NLS and NLW going via 'dls-(bsp|lon)-wb02' instead of directly to 'ld02:8983').  (ld02 being 'lduwka-proxy', our WA infrastructure server that routes all LDL requests onwards to our WA services via Apache httpd proxypasses.)

To set up as a systemctl daemon, as the root user:
* Copy ldl-pusher service file to systemctl directory
 * cp ldl-pusher.service /usr/lib/systemd/system/

* Reload systemctl 
 * systemctl daemon-reload

* Enable and start ldl pusher service
 * systemctl enable --now ldl-pusher.service


Development and Testing
=======================

The service can also be ran manually. It is best to do this as the monitor/dev user and from the user account home directory as this most simulates the production systemctl service operation.

```
~$ /home/<user account>/github/ukwa-monitor/ldl-pusher/run_ldl_pusher.sh
```
