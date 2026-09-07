# wazuh-gworkspace
Wazuh wodle that integrates all Google Workspace audit events (including Drive, Groups, Calendar, SAML and Admin).

![screenshot of Workspace events in Wazuh](/doc/gworkspace%20screenshot.png)

## Advantages with respect to the standard Google GCP integration [provided by Wazuh](https://documentation.wazuh.com/current/cloud-security/gcp/index.html):
* does not require complex Pub / Sub configuration
* integrates **all** auditable Google Workspace events / product types visible in Google Workspace [Reporting](https://admin.google.com/ac/sc/investigation) (i.e. Drive, Calendar, Admin, etc)
* integrates the alerts visible in Google Workspace [Alert Center](https://admin.google.com/ac/ac)
* includes rules with sensible levels (based on the equivalent actions in the O365 integration)

## Disadvantages / limitations:
* only covers Google Workspace audit events and Google Workspace Alert Center, not GCP
* batch-driven instead of event-driven, resulting in a delay between the event and it's recovery
* the `@timestamp` of events is the moment of injection, not the moment of the event, which is stored in `data.timestamp`
* tested on an organisation with 100 users (if you have successfully deployed on a bigger organisation, please let me know)

## Installation:
* [create service account & OAuth client](/doc/install-step-1.md)
* install wodle:
  * [Docker deployment](/doc/install-step-2.md)
  * [direct install on Ubuntu](/doc/install-step-2-Ubuntu-direct.md)

## Frequently Asked Questions

### What if I have several Google Workspace tenants?
Just follow the installation procedure several times. So:
* create a service account in each tenant
* create separate directories
  * /var/ossec/wodles/gworkspace-tenant-A/
  * /var/ossec/wodles/gworkspace-tenant-B/
  * etc
* create the respective service accounts, and place them in the `service_account_key.json` of their directories.
* in `ossec.conf` create separate `<wodle>`entries, where the `<command>`is changed:
```
  <wodle name="command">
    <disabled>no</disabled>
    <tag>gworkspace</tag>
    <command>/var/ossec/wodles/gworkspace-tenant-A/gworkspace -a all -o 2</command>
    <interval>10m</interval>
    <ignore_output>no</ignore_output>
    <run_on_start>yes</run_on_start>
    <timeout>0</timeout>
  </wodle>
```

All the events include a `data.gworkspace.customerId`that identifies the Google Workspace customer. If you want a specific label you can add a `<tag>name</tag>` to the `ossec.conf`.

### Why aren't my gworkspace rules triggering?
Wazuh's `analysisd` loads *all* rule files - the stock ruleset plus everything in your custom rules directory - in a single global alphabetical order by filename, not per-directory. If any of your other custom rule files sort before the stock ruleset (e.g. old `0000_`-`0004_`-style names), rules that depend on a stock rule, directly or transitively, can silently fail to load - `0685-gworkspace_rules.xml` included. Wazuh's error log also caps the errors it reports per file at 50 (`ERRORLIST_MAXSIZE`), so a file that is 100% broken can look like only a handful of rules failed. If your gworkspace alerts are not showing up, check `/var/ossec/logs/ossec.log` for rule-loading warnings after a restart, and if needed rename your custom rule files (e.g. with a `9999_` prefix) so they sort after the entire stock ruleset.

