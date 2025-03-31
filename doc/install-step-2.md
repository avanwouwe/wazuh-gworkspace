> [!NOTE]  
> this wodle works on any Wazuh installation but this how-to assumes a [Wazuh docker deployment](https://github.com/wazuh/wazuh-docker) and may require (slight) adaptation for other deployment methods

# add required Python libraries
The wodle requires the `google-api-python-client` Python library, which is not distributed with the standard Wazuh distribution. To ensure that this library is in the Docker image, first create a custom Dockerfile for the master node. This Dockerfile will build on the standard image provided by Wazuh.

```
cd  ~/wazuh-docker/multi-node/config/wazuh_cluster/
cat > master.Dockerfile << EOF
FROM wazuh/wazuh-manager:4.10.0
RUN /var/ossec/framework/python/bin/python3 -m pip install google-api-python-client
EOF
```

Then change the `docker-compose.yml` to build this custom container instead of using the standard one. Replace this:
```
services:
  wazuh.master:
    image: wazuh/wazuh-manager:4.10.0
```

... with this:
```
services:
  wazuh.master:
    build:
        dockerfile: ./config/wazuh_cluster/master.Dockerfile
```

> [!NOTE]  
> don't forget to update the version numbers of the docker image when you install and whenever you upgrade your installation.

# install wodle
Clone this repo in the directory where the Wazuh docker repo is cloned
```
> ls
wazuh-docker
> git clone https://github.com/avanwouwe/wazuh-gworkspace.git
> ls
wazuh-docker/
wazuh-gworkspace/
```

In the `docker-compose.yml` mount the `/wodle` directory of this repo so that it is available on the Wazuh master.
```
    volumes:
      - ../../wazuh-gworkspace/wodle:/var/ossec/wodles/gworkspace
```

Now you can rebuild the image and recreate the containers to ensure that the python library is installed and the volume is mounted:
```
cd  ~/wazuh-docker/multi-node/
docker compose down
docker compose up -d --build
```

And then create a shell session on the master node:
```
docker ps
docker exec -ti <container id of master container> /bin/bash
cd /var/ossec/wodles/gworkspace/
```

Copy the file with the GCP service account key you have created previously, by pasting the contents of the JSON file after this command, followed by <enter> and <cntrl-D>:
```
cat > service_account_key.json
```

Also configure your Google Workspace service account:
```
cat > config.json << EOF
{
    "service_account": "<E-MAIL OF YOUR GOOGLE WORKSPACE SERVICE ACCOUNT>"
}
EOF
```

You can test that the wodle works by running it and checking that it outputs log events in JSON format. The `--unread` parameter ensures that the historical messages will be left unread for the next run. 
```
./gworkspace -a admin --unread
```

You can then close the shell session.

# add rules
Events only generate alerts if they are matched by a rule. Go to the rules configuration and create a new rules file `0685-gworkspace_rules.xml` and fill it with the contents of [/rules/0685-gworkspace_rules.xml](/rules/0685-gworkspace_rules.xml).

# change ossec.conf
Add this wodle configuration to `/var/ossec/etc/ossec.conf` to ensure that the wodle is called periodically by Wazuh. In the Wazuh-provided Docker installion this file is modified in `~/wazuh-docker/multi-node/config/wazuh_cluster`.
```
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

This will run the wodle every 10 minutes. Running it more often will be more resource-intensive for Google (every run requires at least one API call for each of the 30-odd service types, such as 'Meet', 'Drive', etc) and running it is less often will mean that events arrive with more delay. More delay also means that the `@timestamp` fields are (more) incorrect, since Wazuh does not allow the decoder to map a field to `@timestamp`, but fills it with the time of alert injection. The `data.timestamp`contains the real timestamp of the event. This means the information is retained but the events may show up in the Wazuh dashboards a couple of minutes after their actual occurrence.

The wodle keeps track of the most recent event that has been extracted for each service type, and will start extracting from that time point on at the next extraction. The `-o` parameter configures the offset, or the maximum number of hours to go back in time. If the offset goes back too far in history, the extraction will return a lot of data and may time out the first time you run it. And if the offset is too short it will result in missed events, should the wodle stop running for longth than that period.

Restart the server for the changes to take effect, for example using the `Restart cluster` button in the `Server Management` > `Status` menu.

You should start seeing new events show up in the Threat hunting module. You can filter for `data.gworkspace.application: *` to make it easier to see.

![screenshot of Workspace events in Wazuh](/doc/gworkspace%20screenshot.png)

