


Example output from Heritrix3 API
---------------------------------

The raw JSON from a Heritrix3 crawl job is quite complex. We only extract a few crucial metrics, but can add more later
as needed. The whole JSON record for a job mid-crawl looks like this:

```json
{
    "deployment": "production",
    "function": "ingest",
    "name": "monthly",
    "server": "https://crawler01.bl.uk:8445/",
    "state": {
        "details": {
            "job": {
                "alertCount": "4160",
                "alertLogFilePath": "/heritrix/output/logs/monthly/20171101060126/alerts.log",
                "availableActions": {
                    "value": [
                        "pause",
                        "checkpoint",
                        "terminate",
                        "teardown"
                    ]
                },
                "checkpointFiles": null,
                "configFiles": {
                    "value": [
                        {
                            "editable": "false",
                            "key": "loggerModule.path",
                            "name": "logs subdirectory",
                            "path": "/heritrix/output/logs/monthly/20171101060126",
                            "url": "https://crawler01.bl.uk:8445/engine/job/monthly/engine/anypath//heritrix/output/logs/monthly/20171101060126"
                        },
                        {
                            "editable": "false",
                            "key": "org.archive.modules.deciderules.surt.SurtPrefixedDecideRule#4e63ebd4.surtsDumpFile",
                            "name": "surtsDumpFile",
                            "path": "/jobs/monthly/exclude.dump",
                            "url": "https://crawler01.bl.uk:8445/engine/job/monthly/engine/anypath//jobs/monthly/exclude.dump"
                        }
                    ]
                },
                "crawlControllerState": "RUNNING",
                "crawlLogFilePath": "/heritrix/output/logs/monthly/20171101060126/crawl.log",
                "crawlLogTail": {
                    "value": [
                        "2017-11-14T13:59:48.275Z   200      96510 http://www.hu17.net/wp-content/uploads/2017/05/btley.jpg LELX http://www.hu17.net/2017/05/14/batley-boys-make-blue-golds-pay-for-their-mistakes/ image/jpeg #092 20171114135948129+123 sha1:5TZ64Y25AO7QPVZKXTKIZZ4UBVSLAEKQ http://www.HU17.net ip:174.137.176.100,duplicate:digest {\"contentSize\":96860,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2821627}",
                        "2017-11-14T13:59:36.388Z   302          0 https://www.bloomsbury.com/uk/author/michael-sims LLL https://www.bloomsbury.com/uk/non-fiction/history/ unknown #032 20171114135936326+60 sha1:3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ http://www.bloomsbury.com/ ip:82.196.237.234 {\"contentSize\":158,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2820328}",
                        "2017-11-14T13:59:11.529Z   200       2454 http://www.pinknews.co.uk/images/2017/09/nazir-ali-93x70.jpg LLE http://www.pinknews.co.uk/2017/10/23/ukip-equalities-chief-transgender-political-correctness-is-going-way-too-far/ image/jpeg #059 20171114135911314+208 sha1:XGSSWWMAUFZYWBBQXJJIF25ZSB7MV7CL http://www.pinknews.co.uk/?s=eu+referendum ip:104.20.39.106,duplicate:digest {\"contentSize\":2905,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2818686}",
                        "2017-11-14T13:58:08.696Z   301        686 https://pinterest.com/pin/create/bookmarklet/?url=http%3A%2F%2Fwww.hu17.net%2F2017%2F05%2F14%2Fbatley-boys-make-blue-golds-pay-for-their-mistakes%2F&media=http://www.hu17.net/wp-content/uploads/2017/05/btley.jpg&description=Batley+Boys+Make+Blue+%26+Golds+Pay+For+Their+Mistakes LELL http://www.hu17.net/2017/05/14/batley-boys-make-blue-golds-pay-for-their-mistakes/ text/html #073 20171114135808656+36 sha1:2LQRUNY7WJUKRCIUZGW7S4JPZXVAK55X http://www.HU17.net duplicate:digest,ip:151.101.0.84,2t {\"contentSize\":1363,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2816514}",
                        "2017-11-14T13:58:08.640Z -9998          - https://www.facebook.com/sharer.php?u=http%3A%2F%2Fwww.hu17.net%2F2017%2F05%2F14%2Fbatley-boys-make-blue-golds-pay-for-their-mistakes%2F&t=Batley+Boys+Make+Blue+%26+Golds+Pay+For+Their+Mistakes LELL http://www.hu17.net/2017/05/14/batley-boys-make-blue-golds-pay-for-their-mistakes/ unknown #021 - - http://www.HU17.net 2t {}",
                        "2017-11-14T13:58:08.144Z     1        172 dns:pinterest.com LELLP https://pinterest.com/pin/create/bookmarklet/?url=http%3A%2F%2Fwww.hu17.net%2F2017%2F05%2F14%2Fbatley-boys-make-blue-golds-pay-for-their-mistakes%2F&media=http://www.hu17.net/wp-content/uploads/2017/05/btley.jpg&description=Batley+Boys+Make+Blue+%26+Golds+Pay+For+Their+Mistakes text/dns #007 20171114135808128+16 sha1:XI54ETTCS6SSNO6BEXDWX4PCN5IRXWJC http://www.HU17.net - {\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2816262}",
                        "2017-11-14T13:58:08.125Z     1         66 dns:www.facebook.com LELLP https://www.facebook.com/sharer.php?u=http%3A%2F%2Fwww.hu17.net%2F2017%2F05%2F14%2Fbatley-boys-make-blue-golds-pay-for-their-mistakes%2F&t=Batley+Boys+Make+Blue+%26+Golds+Pay+For+Their+Mistakes text/dns #007 20171114135808110+15 sha1:OLRLJK44HSKV3F7FNB4VLBFFS7NMT6JT http://www.HU17.net - {\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2816012}",
                        "2017-11-14T13:58:08.108Z   200     104297 http://www.hu17.net/2017/05/14/batley-boys-make-blue-golds-pay-for-their-mistakes/ LEL http://www.hu17.net/beverley-sport/rugby-league/page/2/ text/html #007 20171114135807000+898 sha1:PTFKPDV2QKRVD3MKCCWBWAO64P6W75YZ http://www.HU17.net ip:174.137.176.100 {\"contentSize\":104790,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2790012}",
                        "2017-11-14T13:57:56.239Z   302       4929 https://www.bloomsbury.com/filenotfound.aspx?aspxerrorpath=/arthur-sherlock-9781408858554/Bloomsbury.com LLLXR https://www.bloomsbury.com/uk/arthur-sherlock-9781408858554/Bloomsbury.com text/html #011 20171114135756066+171 sha1:RVOUNIRWVAQ6TRRRKRZ6IG3AEG66STW4 http://www.bloomsbury.com/ ip:82.196.237.234 {\"contentSize\":5275,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2786251}",
                        "2017-11-14T13:56:26.992Z   200      25351 http://www.hu17.net/wp-content/uploads/2017/05/braves_rino-400x200.jpg LEE http://www.hu17.net/beverley-sport/rugby-league/page/2/ image/jpeg #011 20171114135626910+71 sha1:G6AXJB3FHQ4TCGHEVYJJ4D64HPVYTVS6 http://www.HU17.net ip:174.137.176.100,duplicate:digest {\"contentSize\":25700,\"warcFilename\":\"BL-20171114120149755-00241-63~ukwa-h3-pulse-monthly~8443.warc.gz\",\"warcFileOffset\":2784769}"
                    ]
                },
                "elapsedReport": {
                    "elapsedMilliseconds": "1151872192",
                    "elapsedPretty": "13d7h57m52s192ms"
                },
                "frontierReport": {
                    "activeQueues": 4.0,
                    "exhaustedQueues": 27566.0,
                    "inProcessQueues": 0.0,
                    "inactiveQueues": 0.0,
                    "ineligibleQueues": 0.0,
                    "lastReachedState": "RUN",
                    "readyQueues": 0.0,
                    "retiredQueues": 619.0,
                    "snoozedQueues": 4.0,
                    "totalQueues": 28189.0
                },
                "hasApplicationContext": "true",
                "heapReport": {
                    "maxBytes": 2863661056.0,
                    "totalBytes": 1645215744.0,
                    "usedBytes": 1476701456.0
                },
                "isLaunchInfoPartial": "true",
                "isLaunchable": "false",
                "isProfile": "false",
                "isRunning": "true",
                "jobLogTail": {
                    "value": [
                        "2017-11-14T13:56:16.050Z WARNING gzip problem; using raw entity instead (in thread 'ToeThread #32: https://www.bloomsbury.com/uk/arthur-sherlock-9781408858554/Bloomsbury.com'; in processor 'extractorHtml')",
                        "2017-11-14T13:47:52.422Z WARNING gzip problem; using raw entity instead (in thread 'ToeThread #46: https://www.bloomsbury.com/uk/steam-titans-9781620409084/Bloomsbury.com'; in processor 'extractorHtml')",
                        "2017-11-14T13:39:27.281Z WARNING gzip problem; using raw entity instead (in thread 'ToeThread #58: https://www.bloomsbury.com/uk/white-rage-9781632864130/Bloomsbury.com'; in processor 'extractorHtml')",
                        "2017-11-14T13:29:22.343Z WARNING gzip problem; using raw entity instead (in thread 'ToeThread #95: https://www.bloomsbury.com/uk/paradise-in-chains-9781632866127/Bloomsbury.com'; in processor 'extractorHtml')",
                        "2017-11-14T13:02:49.751Z WARNING gzip problem; using raw entity instead (in thread 'ToeThread #18: https://www.bloomsbury.com/uk/mecca-9781408835609/Bloomsbury.com'; in processor 'extractorHtml')"
                    ]
                },
                "lastLaunch": "2017-11-01T06:01:24.769Z",
                "launchCount": "1",
                "loadReport": {
                    "averageQueueDepth": 28697.0,
                    "busyThreads": 0.0,
                    "congestionRatio": 1.0,
                    "deepestQueueDepth": 645977.0,
                    "totalThreads": 100.0
                },
                "primaryConfig": "/jobs/monthly/crawler-beans.cxml",
                "primaryConfigUrl": "https://crawler01.bl.uk:8445/engine/job/monthly/jobdir/crawler-beans.cxml",
                "rateReport": {
                    "averageDocsPerSecond": 8.063600340826701,
                    "averageKiBPerSec": 665.0,
                    "currentDocsPerSecond": 0.2294630564479119,
                    "currentKiBPerSec": 21.0
                },
                "reports": {
                    "value": [
                        {
                            "className": "ProcessorsReport",
                            "shortName": "Processors"
                        },
                        {
                            "className": "FrontierSummaryReport",
                            "shortName": "FrontierSummary"
                        },
                        {
                            "className": "ToeThreadsReport",
                            "shortName": "ToeThreads"
                        }
                    ]
                },
                "shortName": "monthly",
                "sizeTotalsReport": {
                    "dupByHash": 454022135629.0,
                    "dupByHashCount": 3813982.0,
                    "notModified": 0.0,
                    "notModifiedCount": 0.0,
                    "novel": 331308235465.0,
                    "novelCount": 5474255.0,
                    "total": 785330371094.0,
                    "totalCount": 9288237.0,
                    "warcNovelContentBytes": 331308138052.0,
                    "warcNovelUrls": 5472252.0
                },
                "statusDescription": "Active: RUNNING",
                "threadReport": {
                    "processors": {
                        "value": "100 noActiveProcessor"
                    },
                    "steps": {
                        "value": "100 ABOUT_TO_GET_URI"
                    },
                    "toeCount": "100"
                },
                "uriTotalsReport": {
                    "downloadedUriCount": 9288237.0,
                    "futureUriCount": 0.0,
                    "queuedUriCount": 114788.0,
                    "totalUriCount": 9403025.0
                },
                "url": "https://crawler01.bl.uk:8445/engine/job/monthly/job/monthly"
            }
        },
        "rate": "0.2",
        "status": "RUNNING",
        "status-class": "status-warning"
    },
    "url": "https://crawler01.bl.uk:8445/"
}
```