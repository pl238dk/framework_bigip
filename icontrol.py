import os
import json
import requests
requests.packages.urllib3.disable_warnings()

from timestamp.timestamp import timestamp

class bigip(object):
	def __init__(self, host, config=None, params={}):
		self.host = host
		if config is None:
			print('[E] No configuration filename not provided')
		else:
			self.load_configuration(config, params=params)
		return
	
	def load_configuration(self, config, params={}):
		if config == 'custom':
            '''
			Requires:
				username - SSO of user
				password - PIN + Token
			'''
			self.authenticate(params)
			return
		config_file = 'configuration.json'
		path = os.path.abspath(__file__)
		dir_path = os.path.dirname(path)
		with open(f'{dir_path}/{config_file}','r') as f:
			raw_file = f.read()
		config_raw = json.loads(raw_file)
		if config not in config_raw['users']:
			print('[E] Configuration not found in configuration.json')
		else:
			connection_info = config_raw['users'][config]
			self.authenticate(connection_info)
		return
	
	def authenticate(self, connection_info):
		self.session = requests.Session()
		self.session.trust_env = False
		proxies = {
			'http':''
		}
		self.session.proxies = proxies
		
		authentication_params = {
			'username':	connection_info['username'],
			'password':	connection_info['password'],
			'loginProviderName':	'tmos',
		}
		
		url = f'https://{self.host}/mgmt/shared/authn/login'
		response_raw = self.session.post(url, json=authentication_params, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] failed logging into {self.host}')
			return
		response_json = json.loads(response_raw.text)
		self.token = {
			'X-F5-Auth-Token': response_json['token']['token']
		}
		self.session.headers.update(self.token)
		return
	
	def get_request(self, url):
		full_url = f'{self.host}{url}'
		response_raw = self.session.get(full_url, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			#self.auto_login()
			#response_raw = self.session.get(full_url, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	def post_request(self, url, data):
		full_url = f'{self.host}{url}'
		response_raw = self.session.post(full_url, json=data, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			#response_raw = self.session.post(full_url, json=data, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	def delete_request(self, url):
		full_url = f'{self.host}{url}'
		response_raw = self.session.delete(full_url, verify=False)
		if response_raw.status_code == 200:
			return response_raw
		elif response_raw.status_code == 401:
			print(f'[W] Received HTTP 401 : {response_raw.text}')
			#response_raw = self.session.delete(full_url, verify=False)
			return response_raw
		else:
			print(f'[W] Received HTTP {response_raw.status_code} with message : {response_raw.text}')
			return response_raw
	
	def get_ltm_features(self):
		target_dir = '/mgmt/tm/ltm/'
		url = f'https://{self.host}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm features for host {self.host} ({response_raw.status_code})')
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
	
	def get_ltm_feature(self, feature):
		ltm_url = '/mgmt/tm/ltm/'
		target_dir = f'{ltm_url}{feature}'
		url = f'https://{self.host}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm feature for host {self.host} : {feature}')
			return response_raw
		response_json = json.loads(response_raw.text)
		return response_json
	
	def get_ltm_feature_stats(self, feature):
		ltm_url = '/mgmt/tm/ltm/'
		target_dir = f'{ltm_url}{feature}/stats'
		url = f'{self.base_url}{target_dir}'
		response_raw = self.session.get(url, verify=False)
		if response_raw.status_code != 200:
			print(f'[E] could not get ltm feature stats for host {self.host} : {feature}')
			return response_raw
		response_json = json.loads(response_raw.text)
		#self.data['stats'][feature] = response_json['entries']
		#return
		return response_json

if __name__ == '__main__':
	host = ''
	b = bigip(host, config='service')
