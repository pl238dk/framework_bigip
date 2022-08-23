import requests
import getpass
import datetime
import json
import time
requests.packages.urllib3.disable_warnings()

from timestamp.timestamp import timestamp

class bigip(object):
	def __init__(self, hostname):
		self.hostname = hostname
		self.base_url = f'https://{hostname}'
		return
	
	def auto_login(self):
		self.session = requests.session()
		url = f'{self.base_url}/mgmt/shared/authn/login'
		un = ''
		pw = ''
		body = {
			'username':un,
			'password':pw,
			'loginProviderName':'tmos',
		}
		response_raw = self.session.post(url, data=json.dumps(body), verify=False)
		if response_raw.status_code != 200:
			print(f'[E] failed logging into {self.hostname}')
			return response_raw
		response_json = json.loads(response_raw.text)
		
		# time stuff
		expiration_timestamp = response_json['token']['expirationMicros']
		expiration_timestamp_pretty = datetime.datetime.fromtimestamp(expiration_timestamp/1000000).strftime('%c')
		
		token = response_json['token']['token']
		print(f'[I] Token {token} expires on {expiration_timestamp_pretty}')
		headers = {
			'X-F5-Auth-Token': token,
			'Content-Type':	'application/json',
		}
		self.session.headers.update(headers)
		return response_raw
	
	def login(self, un):
		self.session = requests.session()
		url = f'{self.base_url}/mgmt/shared/authn/login'
		pw = getpass.getpass('PASSCODE: ')
		body = {
			'username':un,
			'password':pw,
			'loginProviderName':'tmos',
		}
		#response = self.session.post(url, auth=(un, pw), data=json.dumps(body), verify=False)
		response_raw = self.session.post(url, data=json.dumps(body), verify=False)
		if response_raw.status_code != 200:
			print(f'[E] failed logging into {self.hostname}')
			return response_raw
		response_json = json.loads(response_raw.text)
		self.token = {
			'X-F5-Auth-Token': response_json['token']['token']
		}
		self.session.headers.update(self.token)
		return self.token
	
	def get_request(self, url):
		full_url = f'{self.base_url}{url}'
		response_raw = self.session.get(full_url, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			self.auto_login()
			response_raw = self.session.get(full_url, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	def post_request(self, url, data):
		full_url = f'{self.base_url}{url}'
		response_raw = self.session.post(full_url, json=data, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			self.auto_login()
			response_raw = self.session.post(full_url, json=data, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	def delete_request(self, url):
		full_url = f'{self.base_url}{url}'
		response_raw = self.session.delete(full_url, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			self.auto_login()
			response_raw = self.session.delete(full_url, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	@timestamp
	def get_ltm_features(self):
		target_dir = '/mgmt/tm/ltm/'
		url = f'{self.base_url}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm features for host {self.hostname} ({response_raw.status_code})')
			return response_raw
		response_json = json.loads(response_raw.text)
		response_extract = [
			item['reference']['link']
			for item in response_json['items']
			if
			'items' in response_json
		]
		response_features_raw = [
			url.split('/')[6]
			for url in response_extract
			if
			'/' in url
			and
			url.count('/') >= 6
		]
		ltm_features = [
			feature.split('?')[0]
			for feature in response_features_raw
			if
			'?' in feature
		]
		return ltm_features
	
	@timestamp
	def get_ltm_feature(self, feature):
		ltm_url = '/mgmt/tm/ltm/'
		target_dir = f'{ltm_url}{feature}'
		url = f'{self.base_url}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm feature for host {self.hostname} : {feature}')
			return response_raw
		response_json = json.loads(response_raw.text)
		## not sure if returning non-raw response is most beneficial
		'''
		if 'items' in response_json:
			return response_json['items']
		else:
			return response_json
		'''
		return response_json
	
	@timestamp
	def get_ltm_feature_stats(self, feature):
		ltm_url = '/mgmt/tm/ltm/'
		target_dir = f'{ltm_url}{feature}/stats'
		url = f'{self.base_url}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm feature stats for host {self.hostname} : {feature}')
			return response_raw
		response_json = json.loads(response_raw.text)
		#self.data['stats'][feature] = response_json['entries']
		#return
		return response_json
	
	def exec_ping(self, endpoint):
		dir = '/mgmt/tm/util/ping'
		arguments = {
			'command':'run',
			'utilCmdArgs':f'-c 1 -i 10 {endpoint}',
		}
		response = self.post_request(dir, arguments)
		return response
	
	def exec_ls(self, directory):
		dir = '/mgmt/tm/util/bash'
		arguments = {
			'command':'run',
			'utilCmdArgs':f'-c "ls -al {directory}"'
		}
		response = self.post_request(dir, arguments)
		return response
	
	def create_backup(self, filename):
		dir = '/mgmt/tm/sys/ucs'
		arguments = {
			'command':'save',
			'name':filename,
		}
		response = self.post_request(dir, arguments)
		return response
	
	def delete_backup(self, filename):
		dir = f'/mgmt/tm/sys/ucs/{filename}'
		response = self.delete_request(dir)
		return response
	
	@timestamp
	def get_ltm_basics(self):
		output = {}
		ltm_features = self.get_ltm_features()
		for feature in ltm_features:
			# not sure what this does
			#if feature not in self.data:
				#self.get_ltm_list(feature)
			response_json = self.get_ltm_feature(feature)
			#output[feature] = self.data[feature]
			output[feature] = response_json
			'''
			# maybe this isn't the most beneficial, instead grabbing all raw data regardless
			if 'items' in response_json:
				output[feature] = response_json['items']
			else:
				print(f'[W] Could not find items in response for {feature} : {response_json}')
			'''
		print(f'[I] Retrieved features from {self.hostname} : {list(output.keys())}')
		return output
	
	def search_directory(self, string):
		target_dir = '/mgmt/tm/'
		url = f'{self.base_url}{target_dir}'
		response = self.session.get(url, verify=False)
		if response.status_code != 200:
			print(f'[E] could not get directory ({response.status_code})')
			return
		output = [x['link'][17:] for x in self.directory['items'] if string in x['link']]
		return output
		'''
		if not hasattr(self, 'directory'):
			target_dir = '/mgmt/tm/'
			url = f'{self.base_url}{target_dir}'
			response = self.session.get(url, verify=False)
			if response.status_code != 200:
				print(f'[E] could not get directory')
				return
			self.directory = json.loads(response.text)
		output = [x['link'][17:] for x in self.directory['items'] if string in x['link']]
		'''
		return output
	
def pretty_exec(response):
	response_json = json.loads(response.text)
	print(response_json['commandResult'])
	return

def pretty_items(response):
	response_json = json.loads(response.text)
	items = response_json['items']
	for x in items: print(x)
	return

def parse_config(config):
	modules = ['analytics','apm','auth','cli','cm','gtm','ilx','ltm','net','pem','sys','util','vcmp','wam','wom']
	commands = []
	config_lines = config.split('\n')
	single_command = ''
	for line in config_lines:
		if line and line[0].isalpha():
			first_word = line.split(' ')[0]
			if first_word in modules and single_command not in ['','\n']:
				commands.append(single_command)
				single_command = ''
		# first character of line is not alphabet
		single_command += line + '\n'
	#
	commands.append(single_command + '\n')
	return commands

def gen_lb_dict(config_parsed):
	t = {}
	for command in config_parsed:
		csplit = command.split(' ')
		#print(csplit)
		command_type = csplit[0]
		command_subtype = csplit[1]
		if command_type not in t:
			t[command_type] = {}
		if command_subtype not in t[command_type]:
			t[command_type][command_subtype] = []
		t[command_type][command_subtype].append(command)
	return t

if __name__ == '__main__':
	test_f5 = ''
	sso = ''
	f = bigip(test_f5)
	#r = f.login(sso)
	r = f.auto_login()
	print('[I] End')
