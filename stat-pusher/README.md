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
