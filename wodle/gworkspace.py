
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os, sys, json, argparse, tempfile, traceback, random, time
from datetime import datetime, timedelta


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
KEY_FILE_PATH = os.path.join(SCRIPT_PATH, 'service_account_key.json')
STATE_FILE_PATH = os.path.join(SCRIPT_PATH, 'state.json')
CONFIG_FILE_PATH = os.path.join(SCRIPT_PATH, 'config.json')
STR_LAST_ACTIVITY_TIME = 'lastActivityTime'
STR_GWORKSPACE = 'gworkspace'

RESULTS_PER_REQUEST = 800
MAX_API_RETRIES = 5
MAX_ALERT_LENGTH = 5000
GOOGLE_APPLICATIONS = 'access_transparency,admin,calendar,chat,drive,gcp,gplus,groups,groups_enterprise,jamboard,login,meet,mobile,rules,saml,token,user_accounts,context_aware_access,chrome,data_studio,keep,alert'
SCOPES = [
	'https://www.googleapis.com/auth/admin.reports.audit.readonly',
	'https://www.googleapis.com/auth/apps.alerts'
]

parser = argparse.ArgumentParser(description="Export Google Workspace logs of various services such as drive, groups, etc.")
parser.add_argument('--applications', '-a', dest='applications', required=True, help='comma-separated application names, see https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list#ApplicationName, ')
parser.add_argument('--offset', '-o', dest='offset', required=False, default=24, type=int, help='maximum number of hours to go back in time')
parser.add_argument('--unread', '-u', dest='unread', action='store_true', help='export events but keep them marked as unread') 
args = parser.parse_args()

RESULTS = tempfile.TemporaryFile(mode='w+')

with open(CONFIG_FILE_PATH, 'r') as config_file:
	CONFIG = json.load(config_file)


def main():
	if args.applications == "all":
		args.applications = GOOGLE_APPLICATIONS

	scoped_applications = args.applications.split(',')

	for application in scoped_applications:
		if application not in  GOOGLE_APPLICATIONS.split(','):
			fatal_error('unknown application type "{}"'.format(application))

	offset_time = datetime.now() - timedelta(hours = args.offset)
	offset_time = as_iso8601(offset_time)

	state = load_state()

	for application in scoped_applications:
		earliest_time = dict_path(state, application, STR_LAST_ACTIVITY_TIME) or offset_time

		if application == 'alert':
			service = get_service('alertcenter', 'v1beta1')
			get_alerts(service, earliest_time)
		else:
			service = get_service('admin', 'reports_v1')
			get_logs(service, application, earliest_time)

	if not args.unread:
		update_state()

	print_results()

	json_msg('extraction', 'finished', 'message', "extraction finished")


def get_service(service_name, service_version):
	"""builds the service used to query Google

	Returns:
		 Resource:   A Resource object with methods for interacting with the service.

	"""
	credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH, scopes=SCOPES)
	credentials = credentials.with_subject(CONFIG['service_account'])

	return build(service_name, service_version, credentials=credentials, num_retries=MAX_API_RETRIES)


def dict_path(dictionary, *path):
	curr_element = dictionary

	for idx, key in enumerate(path):
		curr_element = curr_element.get(key)
		if (idx == len(path) - 1):
			break

		if (curr_element == None or not isinstance(curr_element, dict)):
			return None

	return curr_element


def get_retry(service, method_name, params, retries):
	try:
		method = getattr(service, method_name)
		return method().list(**params).execute(num_retries = 0)    # don't use inbuilt retry, does not work
	except:
		if (retries > 0):
			backoff = 2 ** (MAX_API_RETRIES - retries)
			time.sleep(backoff)

			return get_retry(service, method_name, params, retries - 1)
		else:
			raise

def get_logs(service, application, earliest_time):
	nextToken = get_log_page(service, application, earliest_time)

	while (nextToken):
		nextToken = get_log_page(service, application, earliest_time, nextToken)

def get_log_page(service, application, earliest_time, nextToken = None):
	params = {
		'userKey': 'all',
		'startTime': earliest_time,
		'applicationName': application,
		'maxResults': RESULTS_PER_REQUEST
	}

	if (nextToken):
		params['pageToken'] = nextToken

	results = get_retry(service, 'activities', params, MAX_API_RETRIES)

	for activity in results.get('items', []):
		for event in activity.get('events', []):
			timestamp = dict_path(activity, 'id', 'time')

			# search API returns "greater than or equal", but those that are equal were in previous run
			# so exclude them from the result
			if timestamp == earliest_time:
				continue

			converted_event = { }
			converted_event['srcip'] 	= dict_path(activity, 'ipAddress')
			converted_event['user'] 	= dict_path(activity, 'actor', 'email')
			converted_event['id']           = dict_path(activity, 'id', 'uniqueQualifier')
			converted_event['timestamp']	= timestamp

			data = {  }
			converted_event[STR_GWORKSPACE] = data
			data['profileId'] 		= dict_path(activity, 'actor', 'profileId')
			data['customerId']              = dict_path(activity, 'id', 'customerId')
			data['application']	 	= capitalize(dict_path(activity, 'id', 'applicationName'))
			data['eventtype'] 		= capitalize(dict_path(event, 'type'))
			data['eventname'] 		= capitalize(dict_path(event, 'name'))

			converted_parameters = {}
			for parameter in event.get('parameters') or {}:
				for key, value in parameter.items() or {}:
					converted_value = None
					if (key == 'name'):
						name = value
					elif (key in ['value', 'multiValue', 'boolValue', 'intValue','multiIntValue']):
						converted_value = value 
					else:
						converted_value = json.dumps(value)

					converted_parameters[name] = converted_value

			data['parameters'] = converted_parameters

			json.dump(converted_event, RESULTS, indent = None)
			RESULTS.write("\n")

	return results.get('nextPageToken')

def get_alerts(service, earliest_time):
	nextToken = get_alerts_page(service, earliest_time)

	while (nextToken):
		nextToken = get_alerts_page(service, earliest_time, nextToken)

def get_alerts_page(service, earliest_time, nextToken = None):
	params = {
		'filter': f'startTime > "{earliest_time}"'
	}

	if (nextToken):
		params['pageToken'] = nextToken

	results = get_retry(service, 'alerts', params, MAX_API_RETRIES)

	for alert in results.get('alerts', []):
		timestamp = dict_path(alert, 'startTime')

		converted_event = { }
		converted_event['id']			= dict_path(alert, 'alertId')
		converted_event['timestamp']	= timestamp

		email = dict_path(alert, 'data', 'email') or dict_path(alert, 'data', 'actorEmail')
		if email:
			converted_event['user'] = email

		data = {  }
		converted_event[STR_GWORKSPACE] = data
		data['application']		= 'alert'
		data['customerId']		= dict_path(alert,'customerId')
		data['eventtype']		= capitalize(dict_path(alert, 'source'))
		data['eventname']		= capitalize(dict_path(alert, 'type'))

		json_alert = json.dumps(dict_path(alert, 'data'))
		if len(json_alert) > MAX_ALERT_LENGTH:
			json_alert = json_alert[:MAX_ALERT_LENGTH] + "..."

		data['parameters'] = { 'alert' : json_alert}

		json.dump(converted_event, RESULTS, indent = None)
		RESULTS.write("\n")

	return results.get('nextPageToken')

def as_iso8601(datetime):
	return datetime.isoformat() + "Z"

def log_entry(obj):
	return json.dumps(obj)

def capitalize(str):
	if str is None:
		return str
	else:
		return str.replace('_', ' ').lower()

def print_results():
	RESULTS.seek(0)

	for line in RESULTS:
		event = json.loads(line)
		print(log_entry(event))

def load_state():
	if not os.path.exists(STATE_FILE_PATH):
		return {}

	with open(STATE_FILE_PATH, 'r') as f:
		return json.load(f)

def save_state(state):
	with open(STATE_FILE_PATH + '.tmp', 'w+') as newfile:
		json.dump(state, newfile, indent = 3)
		newfile.write("\n")
		os.replace(newfile.name, STATE_FILE_PATH)


def update_state():
	global_state = load_state()

	RESULTS.seek(0)

	for line in RESULTS:
		activity = json.loads(line)
		application = dict_path(activity, STR_GWORKSPACE, 'application')
		activityTime = dict_path(activity, 'timestamp')
		if (application == None or activityTime == None):
			warning('missing "application" or "timestamp" for activity:\n{}'.format(activity))

		application_state = global_state.setdefault(application, { STR_LAST_ACTIVITY_TIME: '0000-00-00T00:00:00.000Z' })
		if (application_state[STR_LAST_ACTIVITY_TIME] < activityTime):
				application_state[STR_LAST_ACTIVITY_TIME] = activityTime
				global_state[application] = application_state

	save_state(global_state)

def json_msg(event_type, event_name, parameter_name, parameter_value):
	msg = {
		'id' : random.randint(0, 99999999999999),
		STR_GWORKSPACE : {
			'application' : 'wazuh extraction',
			'eventtype' : event_type,
			'eventname' : event_name,
			'parameters' : {
				'name' : parameter_name,
				'value' : parameter_value
			}
		}
	}

	print(log_entry(msg))


def fatal_error(message):
	json_msg('extraction', 'extraction error', 'message', message)

	sys.exit(0)   # not 1, otherwise the output will be ignored by Wazuh

def warning(message):
	json_msg('extraction', 'extraction warning', 'message', message)


if __name__ == '__main__':
	try:
		main()
	except Exception as exception:
		fatal_error("fatal exception :\n" + traceback.format_exc())
