# wazuh-gworkspace
Wazuh wodle that integrates all Google Workspace audit events (including Drive, Groups, Calendar, SAML and Admin).

![screenshot of Workspace events in Wazuh](/doc/gworkspace%20screenshot.png)

Advantages with respect to the standard Google GCP integration [provided by Wazuh](https://documentation.wazuh.com/current/cloud-security/gcp/index.html):
* does not require complex Pub / Sub configuration
* integrates **all** auditable Google Workspace events / product types (i.e. Drive, Groups, Calendar, Admin, etc)
* includes rules with sensible levels (based on the equivalent actions in the O365 integration)

Disadvantages / limitations:
* only covers Google Workspace events, not GCP
* the `@timestamp` of events is the moment of injection, not the moment of the event, which is stored in `data.timestamp`

Getting started:
* [create service account & oAuth client](/doc/install-step-1.md)
* [install wodle](/doc/install-step-2.md)
* [install rules](/doc/install-step-3.md)
