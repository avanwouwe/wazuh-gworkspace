# create an GCP service account
First you will create a **GCP service account**. This service account will use **Domain-wide delegation** to impersonate a **Google Workspace service account** to access to the events and alerts.

At [https://console.cloud.google.com/](https://console.cloud.google.com/) create a new project called `Wazuh`.

![screenshot of create project in GCP](/doc/create%20project%20screenshot.png)

In the [Enabled API & services](https://console.cloud.google.com/apis/library) enable:
* the [Admin SDK API](https://console.cloud.google.com/apis/library/admin.googleapis.com) 
* the [Alert Center API](https://console.cloud.google.com/apis/api/alertcenter.googleapis.com)

In the [API & Services menu](https://console.cloud.google.com/apis) select the [Credentials screen](https://console.cloud.google.com/apis/credentials) and create a **service account** with an **Service account name** of for example `Wazuh monitoring`. You will need the `client id` later on.

Once the service account is created, select the "Keys" option from the horizontal menu, and add a key. Be sure to save the key in your password manager since you cannot download it afterwards.

# create a Google Workspace service account
Now, in the Google Workspace admin allow the GCP service account [Domain-wide delegation](https://admin.google.com/ac/owl/domainwidedelegation) by entering the `client id`, and giving it two scopes:
* `https://www.googleapis.com/auth/admin.reports.audit.readonly`
* `https://www.googleapis.com/auth/apps.alerts`

Then you will create a Google Workspace service account that will serve as a service account used by Wazuh to connect. We will make sure to not give this account a Google Workspace licence, both for financial and security reasons.

In the [Organizational units](https://admin.google.com/ac/orgunits) screen create an OrgUnit called `Service accounts`.

Change the [Licence settings](https://admin.google.com/ac/billing/licensesettings) for that OrgUnit so that licenses are not automatically assigned. Note that the sliders do not appear until your mouse is over the option.

![screenshot of licence settings](/doc/google%20licence%20settings.png)

Create a new user in that OrgUnit, naming it for example **First name** `SVC Wazuh` and **Last name** `Monitoring` with an e-mail address of `svc-wazuh-monitoring@yourdomain.com`. 
* in **Admin roles and privileges** 
  * in `Alert Center` check `View access`
  * check the `Reports` role
* in **Licences** double-check that the user does not have a paying licence
* in **Apps** double-check that the user does not have access to apps that it shouldn't
* you can throw away the password for that user, it will be the GCP service account that impersonates this user

Depending on your MFA policies you may also need to change other OrgUnit-wide settings for the OrgUnit, so that you can turn off **2-step verification** or **require password change** in the **Security** tab sheet.

Hope you kept the JSON file containing the key of the GCP service account, you will use it in the [next step](/doc/install-step-2.md).

![screenshot of user settings](/doc/google%20user%20settings.png)

