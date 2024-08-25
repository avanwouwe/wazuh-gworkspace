# create a service account
First you will create a Google Workspace account that will serve as a sevice account used by Wazuh to connect. We will make sure to not give this account a Google Workspace licence, both for financial and security reasons.

In the [Organizational units](https://admin.google.com/ac/orgunits) screen create an OrgUnit called `Service accounts`.

Change the [Licence settings](https://admin.google.com/ac/billing/licensesettings) for that OrgUnit so that licenses are not automatically assigned. Note that the sliders do not appear until your mouse is over the option.

![screenshot of licence settings](/doc/google%20licence%20settings.png)

Create a new user in that OrgUnit, naming it for example **First name** `SVC Wazuh` and **Last name** `Monitoring` with an e-mail address of `svc-wazuh-monitoring@yourdomain.com`. 
* in **Admin roles and privileges** check the `Reports` role
* in **Licences** double-check that the user does not have a paying licence
* in **Apps** double-check that the user does not have access to apps that it shouldn't

Depending on your policies you may also need to change other OrgUnit-wide settings for the OrgUnit, so that you can turn off **2-step verification** or **require password change** in the **Security** tab sheet.

![screenshot of user settings](/doc/google%20user%20settings.png)


# create an OAuth client
At [https://console.cloud.google.com/](https://console.cloud.google.com/) create a new project called `Wazuh`.

![screenshot of create project in GCP](/doc/create%20project%20screenshot.png)

In the [Enabled API & services](https://console.cloud.google.com/apis/library) enable the [Admin SDK API](https://console.cloud.google.com/apis/library/admin.googleapis.com?project=wazuh-413509)
In the [API & Services menu](https://console.cloud.google.com/apis) select the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) and create an **internal** user type and with an **App name** of for example `Wazuh monitoring`. Then click ***SAVE AND CONTINUE***.

In the **Scopes** screen, add the scope `https://www.googleapis.com/auth/admin.reports.audit.readonly`. Then click ***SAVE AND CONTINUE***.

In the [Credentials screen](https://console.cloud.google.com/apis/credentials) create an **OAuth client ID** of type `Web application`. Set the **Name** of the client to `Wazuh monitoring` and add as **Authorized redirect URI** the URL `http://localhost:8888/` (note the trailing slash).

Download the JSON containing the Client secret, you will use it in the [next step](/doc/install-step-2.md).
![Google OAuth client created](/doc/google%20oauth%20client%20created.png)
