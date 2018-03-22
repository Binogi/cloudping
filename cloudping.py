from __future__ import unicode_literals

import requests
import json
import boto3
import datetime


def ping(event, context):
    """Ping the status of a webpage."""
    options = {
        'domain': 'example.com',
        'protocol': 'http',
        'path': '/',
        'method': 'GET',
        'allow_redirects': False,
        'timeout': 5,
    }
    options.update(event)
    url = '{protocol}://{domain}{path}'.format(**options)

    try:
        response = requests.request(
            options['method'],
            url,
            allow_redirects=options['allow_redirects'],
            timeout=options['timeout'])
        response.raise_for_status()
        result_value = 0
    except Exception as e:
        print(str(e))
        result_value = 1

    print(json.dumps({
        'cloudping_result': result_value,
        'url': url,
        'options': options
    }))

    client = boto3.client('cloudwatch')
    response = client.put_metric_data(
        Namespace='cloudping',
        MetricData=[
            {
                'MetricName': 'status',
                'Dimensions': [
                    {
                        'Name': 'url',
                        'Value': url
                    },
                    {
                        'Name': 'method',
                        'Value': options['method']
                    },
                    {
                        'Name': 'protocol',
                        'Value': options['protocol']
                    },
                ],
                'Timestamp': datetime.datetime.utcnow(),
                'Value': result_value,
                'Unit': 'None',
                'StorageResolution': 60
            },
        ]
    )
