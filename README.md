# F5 Framework for BIG-IP

This is a framework that connects to an F5 iControl REST API.

## Authentication

Credentials are stored in JSON format, in the same directory as the `icontrol.py` file. The name of the file should be `credentials.json`.

Other authentication methods, such as KDBX, have been tested, but this way it keeps the hard-coded passwords out of the source code.

```
{
	"users":	{
		"arbitrary_name": {
			"username":	"",
			"password":	""
		}
	}
}

```

The name of the credentials is arbitrary and references parameters for username and password.

## Getting Started

To instantiate a `bigip` object, pass a string of the credential name created in the "Authentication" section :

```
>>> bigip_host = 'ltm01'
>>> credential_name = 'arbitrary_name'
>>> b = bigip(bigip_host, config=credential_name)
```

The object instantiation will automatically log in and re-authenticate whenever the session timeout expires.

## iControl REST API Features

As of the most recent update, grabbing LTM data is the only feature currently explored.

This is an extremely simplistic API to navigate for basic data retrieval.

To list all available features of an LTM appliance :

```
>>> features = b.get_ltm_features()
```

To grab a specific feature of an LTM appliance, such as a list of Pools :

```
>>> feature = 'pool'
>>> data = b.get_ltm_feature(feature)
```

To retrieve statistics of a specific LTM feature, such as a Pool, find the UID :

```
>>> uid = '1234567'
>>> feature = 'pool/' + uid
>>> data = b.get_ltm_feature_stats(feature)
```