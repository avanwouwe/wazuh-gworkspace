> [!NOTE]  
> this wodle works on any Wazuh installation but this how-to assumes a [Wazuh direct install on Ubuntu](https://documentation.wazuh.com/current/installation-guide/index.html)

# add required Python libraries
The wodle requires the `google-api-python-client` Python library, which is not distributed with the standard Wazuh distribution. Run the following command to install.

```
/var/ossec/framework/python/bin/python3 -m pip install google-api-python-client
```

# install wodle
Clone this repo into any directory (for this how-to /root is used)
```
git clone https://github.com/avanwouwe/wazuh-gworkspace.git
> ls
wazuh-gworkspace/
```

create an new directory for the wodle and copy files.
```
> mkdir /var/ossec/wodles/gworkspace
> cd /wazuh-gworkspace/wodle
> cp * /var/ossec/wodles/gworkspace
> ls /var/ossec/wodles/gworkspace
gworkspace  gworkspace.py
```

Change to the new directory. Copy contents of the file with the GCP service account key you have created previously, and paste the contents of the JSON file after this command, followed by <ctrl-o> and <ctrl-x>:
```
> cd /var/ossec/wodles/gworkspace
> nano service_account_key.json
```

Also paste the following modified with your service account to configure your Google Workspace service account, followed by <ctrl-o> and <ctrl-x>:
```
> nano config.json
{
    "service_account": "<E-MAIL OF YOUR GOOGLE WORKSPACE SERVICE ACCOUNT>"
}
```

You can test that the wodle works by running it and checking that it outputs log events in JSON format. The `--unread` parameter ensures that the historical messages will be left unread for the next run. 
```
> ./gworkspace -a admin --unread
```

# add rules
Events only generate alerts if they are matched by a rule. Copy the rules configuration file `0685-gworkspace_rules.xml` to the rules directory.
```
> cd /root/wazuh-gworkspace/rules/
> cp * /var/ossec/ruleset/rules/
```

# change ossec.conf
Add this wodle configuration to `/var/ossec/etc/ossec.conf` to ensure that the wodle is called periodically by Wazuh, followed by <ctrl-o> and <ctrl-x>. 
```
> nano /var/ossec/etc/ossec.conf
  <wodle name="command">
    <disabled>no</disabled>
    <tag>gworkspace</tag>
    <command>/var/ossec/wodles/gworkspace/gworkspace -a all -o 2</command>
    <interval>10m</interval>
    <ignore_output>no</ignore_output>
    <run_on_start>yes</run_on_start>
    <timeout>0</timeout>
  </wodle>
```
Restart the server for the changes to take effect.

```
systemctl restart wazuh-manager
```

> [!NOTES] 

This will run the wodle every 10 minutes. Running it more often will be more resource-intensive for Google (every run requires at least one API call for each of the 30-odd service types, such as 'Meet', 'Drive', etc) and running it is less often will mean that events arrive with more delay. More delay also means that the `@timestamp` fields are (more) incorrect, since Wazuh does not allow the decoder to map a field to `@timestamp`, but fills it with the time of alert injection. The `data.timestamp`contains the real timestamp of the event. This means the information is retained but the events may show up in the Wazuh dashboards a couple of minutes after their actual occurrence.

The wodle keeps track of the most recent event that has been extracted for each service type, and will start extracting from that time point on at the next extraction. The `-o` parameter configures the offset, or the maximum number of hours to go back in time. If the offset goes back too far in history, the extraction will return a lot of data and may time out the first time you run it. And if the offset is too short it will result in missed events, should the wodle stop running for longth than that period.

You should start seeing new events show up in the Threat hunting module. You can filter for `data.gworkspace.application: *` to make it easier to see.

![screenshot of Workspace events in Wazuh](/doc/gworkspace%20screenshot.png)

