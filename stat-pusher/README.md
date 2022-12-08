Stats Pusher
============

Add new stats metrics to `dev.stats`, then use a pull-request to add them in. They should then be deployed across `beta` and then `prod`.

To test them on the `dev` server, we need a `virtualenv`:

```
$ virtualenv -p python3 venv
```

Then run:

```
$ run_stat_pusher.sh dev
```

Which should grab the stats and push them to the DEV monitor. It relies on `gitlab/ukwa-monitor` to pick up environment variables.



LDL VM Monitoring Pusher
========================

We've always had difficulties tracking the status of DLS LDL VMs, especially their network connectivity.

Each LDL VM (except NLW as of 2022 Nov 7) now has a root cronjob that curls "http://ld02:8983/wa/monitor?host=$(hostname -f)" (NLS and
NLW going via 'dls-(bsp|lon)-wb02' instead of directly to 'ld02:8983').

(ld02 being 'lduwka-proxy', our WA infrastructure server that routes all LDL requests onwards to our WA services via Apache httpd proxypasses.)

Consequently, the ldl-pusher.py script runs as a daemon, accepts these curl requests, and pushes them into prometheus.
