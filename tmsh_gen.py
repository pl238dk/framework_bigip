def create_monitor(url,protocol):
	'''
	create /ltm monitor https MON_{protocol} {{
		adaptive disabled
		defaults-from https
		destination *:*
		interval 5
		ip-dscp 0
		recv none
		recv-disable none
		send "GET / HTTP/1.1\\r\\nHost: {url}\\r\\nConnection: Close\\r\\n\\r\\n"
		ssl-profile /Common/serverssl
		time-until-up 5
		timeout 16
	}}
	'''
	if protocol == 'http':
		output = f'create /ltm monitor http MON_{url.upper()}  {{ adaptive disabled defaults-from http destination *:* interval 5 ip-dscp 0 recv none recv-disable none send "GET / HTTP/1.1\\r\\nHost: {url}\\r\\nConnection: Close\\r\\n\\r\\n" time-until-up 5 timeout 16 }}'
	elif protocol == 'https':
		output = f'create /ltm monitor https MON_{url.upper()} {{ adaptive disabled defaults-from https destination *:* interval 5 ip-dscp 0 recv none recv-disable none send "GET / HTTP/1.1\\r\\nHost: {url}\\r\\nConnection: Close\\r\\n\\r\\n" ssl-profile /Common/serverssl time-until-up 5 timeout 16 }}'
	return output

def create_node(hostname, ip, rd):
	output = f'create /ltm node {hostname.upper()}_RD{rd} {{ address {ip}%{rd} }}'
	return output

def create_pool(host,description,members,rd):
	'''
	create /ltm pool PL_{host}_80 {
		description "{description}"
		members add {
			{name}:80 { address {ip} }
			{name}:80 { address {ip} }
			{name}:80 { address {ip} }
		}
		monitor {monitor}
	}
	'''
	member_config = ' '.join([f'{member[0]}:80 {{ address {member[2]:{rd}} }}' for member in members])
	output = f'create /ltm pool PL_{host.upper()}_80 {{ description "{description}" members add {{ {member_config} }} monitor MON_{host.upper()} }}'
	return output

def create_irule_host(host):
	'''
	elseif {
		[string tolower [HTTP::host]] equals "{host}"
	} {
		pool  "PL_{host}_80"
	}
	'''
	output = f'elseif {{ [string tolower [HTTP::host]] equals "{host}" }} {{\r\n\tpool "PL_{host}_80"\r\n}}'
	return output

def create_irule_redirect(host):
	'''
	elseif {
		[string tolower [HTTP::host]] equals "{host}"
	} {
		HTTP::respond 301 Location "https://{host}"
	}
	'''
	output = f'elseif {{ [string tolower [HTTP::host]] equals "{host}" }} {{\r\n\tHTTP::respond 301 Location "https://"{host}"\r\n}}'
	return output

print('[I] Begin')
urls = [
    'google.com',
    'microsoft.com',
    'amazon.com',
]
print('[I] End')