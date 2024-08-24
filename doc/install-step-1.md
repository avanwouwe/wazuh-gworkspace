# create a service account
First you will create a Google Workspace account that will serve as a sevice account used by Wazuh to connect. We will make sure to not give this account a Google Workspace licence, both for financial and secutity reasons.

In the [Organizational units](https://admin.google.com/ac/orgunits) screen create an OrgUnit called `Service accounts`.

Change the [Licence settings](https://admin.google.com/ac/billing/licensesettings) for that OrgUnit so that licenses are not automatically assigned. Note that the sliders do not appear until your mouse is over the option.

![screenshot of licence settings](/doc/google%20licence%20settings.png)

Create a new user in that OrgUnit, naming it for example `SVC Wazuh Monitoring` with an e-mail address of `svc-wazuh-monitoring@yourdomain.com`. Double-check that the user does not have a paying licence.

# create an OAuth client
At [https://console.cloud.google.com/](https://console.cloud.google.com/) create a new project called `Wazuh`.

![screenshot of create project in GCP](/doc/create%20project%20screenshot.png)

In the [API & Services menu](https://console.cloud.google.com/apis) select the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) and create an **internal** user type and with an **App name** of for example `Wazuh monitoring`. Then click ***SAVE AND CONTINUE***.

In the **Scopes** screen, add the scope `https://www.googleapis.com/auth/admin.reports.audit.readonly`. Then click ***SAVE AND CONTINUE***.

In the [Credentials screen](https://console.cloud.google.com/apis/credentials) create an **OAuth client ID** of type `Web application`. Set the **Name** of the client to `Wazuh monitoring` and add as **Authorized redirect URI** the URL `http://localhost:8888/` (note the trailing slash).

Download the JSON containing the Client secret, you will use it in the [next step](/doc/install-step-2.md).
![Google OAuth client created](/doc/google%20oauth%20client%20created.png)