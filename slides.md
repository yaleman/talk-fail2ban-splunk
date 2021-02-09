---
highlight: yalecustom
theme: darkgrey
progress: true
controls: false
# cube, page, concave, zoom, linear, fade, none, default 
transition: none
slideNumber: false
editor:
  hidden: true
speaker-layout: notes-only
---

---
# How to (not) fail2ban with Splunk 

Sharing is caring!

Notes:
* how to not fail2ban with splunk
* or socialising threat data across your fleet
---
# who?

### James Hodgkinson

"security team"

Notes:
* security team
* domain registrar and web hosting company
* previously for emergency services
* 💜 splunking all the things
---
## Derpy.

![jobs](/images/splunkjobs.png)

Notes:
* pulling the splunk jobs feed
* searchable
* alerting
---

## Really derpy.

![safaritabs](/images/safaritabs.png)

---
## tl;dr

- fail2ban?
- The problem.
- "*The Solution*"
- Idea!
- The *actual* solution.

Notes:
* what is fail2ban?
* what was our problem
* the original solution
* the idea
* the actual solution
--- 

## fail2ban?

```shell
$ man fail2ban

A set of server and client programs to limit 
brute force authentication attempts.
```

---
## fail2ban.

🐍 Written in python.

🌏 Available *everywhere*.

🪵 Filters logs with 🪄regex🪄

🏃‍♂️ Runs actions.

👮‍♀️ Puts IPs in jails.


Notes:
* written in python
* packaged or manually installable
* parses logs with the magic of regex
* configurable "actions"
* keeps track of those actions by putting IPs in "jails"
* the only problem is that it  only runs locally

---
## fail2ban.

🐍 Written in python.

🌏 Available *everywhere*.

🪵 Filters logs with 🪄regex🪄

🏃‍♂️ Runs actions.

👮‍♀️ Puts IPs in jails.

😢 Local-only.

Notes:
* written in python
* packaged or manually installable
* parses logs with the magic of regex
* configurable "actions"
* keeps track of those actions by putting IPs in "jails"
* the only problem is that it  only runs locally
---

## 🏃‍♂️ Actions

- iptables
- Cloudflare
- Netscaler
- Logging
- ???
- other

Notes:
* whole bunch of different options
* shell scripts 
* do this to start
* undo this at end

---

## 👮‍♀️ Jails!

- Enforce "action" for "time".
- Automatic cleanup.
- Scales response on repeat offenders.

Notes:
* internal concept
* tracks IPs
* time
* multiple jails
  * ssh apache, wordpress
  * start and end actions actions
  * different times
* great benefit is that it can scale its response over time
  * random IP xyz
  * blocked once for an hour
  * comes back
  * block for four hours
 * wordpress for a week
---

## Configuring fail2ban

```shell
$ cat /etc/fail2ban/jail.d/mywebapp.conf

[mywebapp]

logpath = /var/log/mywebapp.log
port = http,https

[splunk]

enabled = true
port = http,https
protocol = tcp
bantime = 3600
banaction = iptables-multiport
action=%(banaction)s[bantime="%(bantime)s",port="%(port)s",protocol="%(protocol)s"]
```

Notes:
* my example
* can set whatever services
* doesn't even have to be the ports the app runs on
* iptables EVERYTHING

---

## Filters

### 🪄 regex! 🪄

![regex](/images/magic.gif)

Notes:
* use regex
* find badness
* source IP
* logs since last check
---

## Configuring fail2ban

```shell
$ cat /etc/fail2ban/filter.d/mywebapp.conf

[Definition]
failregex = ^HACKER ATTEMPT FROM \[HOST\]$
```

Notes:
* patterns
* lots of defaults
* apache, ssh, squid, counter-strike
---

## The Problem.

 * cPanel hosting.
 * Hundreds of servers.
 * Low budget.

Notes:
* fleet that this system is for
* cpanel
  * if you haven't heard of it hosting control-panel
  * users and resellers to manage their hosting
  * apache, php, mysql, mail etc
* many hundreds
  * AWS
  * on prem
  * disparate fleets with different technologies
* attacks and scans across multiple hosts
  * new wordpress vulnerability
  * 35% of the internet
  * shodan google whatever
* we're not enterprise hosting
* retail
---
# "The Solution"

Notes:
* as "the security guy", I wasn't the first
* someone else had built a thing
* had interesting ideas
* didn't work
* why?
---
![fail2ban cluster diagram](/images/Fail2banCluster-Diagram.jpg)

Notes:
- fail2ban calls a script
- pushes to SNS
- which pushes to an SQS queue *for* every server
- picked up by each server
- back into fail2ban
- scaling?
- troubleshooting?
- cost?

---
![stop.](/images/stop-to-think.jpg)

Notes:
* hmm
* didn't work
* problems on the platform
* start again
--- 

## Facts

- Quick 🔥💻🔥
- Multi-cloud.
- No major platform changes.
- Low signal:noise.
- Huge log volume.
- I'm terrible.

Notes:
* we needed it quick
* AWS and on-premises
  * can't use WAF/NACLs
  * ASA's or F5's
* weren't going to rebuild it all from scratch
* Log *volume* meant we can't just Splunk it (sorry Jody 😋)
* Log count would punish splunk forwarder
  * 100ish? KB of memory to a meg or so per file
* can't chase it around
* I'm terrible, i'm the splunk guy, solve it with splunk
---


## New plan?

Notes:
* fail2ban is great
* quick
* configurable
* parses logs
* does things
* problem
* local only
* need to socialise data

---

## An idea

 1. fail2ban parses logs
 3. Writes *more specific* logs
 4. Splunk collects those logs
 5. Writes a csv to a public s3 bucket
 7. Servers collect, parse and feed to fail2ban

Notes:
* parse logs
* takes actions
* also writes logs
* splunk
* search */10
* custom alert action
* csv -> s3
* script on server which grabs + bans
* block for x time

---

## I *told* you I was terrible.

---
![Final - Step 1](/images/prod_implementation1.png)

Notes:

hackers attack the web servers
---
![Final - Step 2](/images/prod_implementation2.png)

Notes:

fail2ban identifies it, blocks the IP and writes a log
---
![Final - Step 3](/images/prod_implementation3.png)

Notes:

writes a log that ends up in splunk
---
![Final - Step 4](/images/prod_implementation4.png)

Notes:
* which goes to s3
* and then the server picks it up
* REMEMBER TO USE A DIFFERENT JAIL!

---

## it works!


Notes:

* couple of hours work
* app builder -> alert action
* made sure it wasn't blowing things up straight away
* rolled out everywhere
* left it a day
* thousands

fail2ban-client set $jail banip $ip
---

## it works!

```shell
$ sudo fail2ban-client status splunk
Status for the jail: splunk
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:
`- Actions
   |- Currently banned:	4578
   |- Total banned:	513962
   `- Banned IP list: *many, many IPs*
```
---

## it works!

```shell
$ sudo fail2ban-client status
Status
|- Number of jail:	6
`- Jail list:	apache-wordpress, apache-wordpress-24h,
cphulk-mail, exim, modsec, splunk
```

---

## summary

 - fail2ban
 - Splunk
 - s3
 - 🪄
 - win!

Notes:

* fail2ban is handy
* splunk is great
* s3 is a very flexible file store
* add magic
* win!

---

## fin

Questions?

####  github.com/yaleman/talk-fail2ban-splunk

![slides QR code](/images/slide-qr-code.png)

---
