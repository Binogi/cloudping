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
        'verify_response_contains': '',
    }
    options.update(event)
    url = '{protocol}://{domain}{path}'.format(**options)
    response_time = None

    try:
        response = requests.request(
            options['method'],
            url,
            allow_redirects=options['allow_redirects'],
            timeout=options['timeout'])
        response.raise_for_status()
        response_time = response.elapsed.total_seconds()
        if options['verify_response_contains'] in response.text:
            result_value = 0
        else:
            print("Could not find required string in response", response.text)
            result_value = 1
    except Exception as e:
        print(str(e))
        result_value = 1

    print(json.dumps({
        'cloudping_result': result_value,
        'response_time': response_time,
        'url': url,
        'options': options
    }))

    client = boto3.client('cloudwatch')
    dimensions = [
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
    ]
    timestamp = datetime.datetime.utcnow()
    #client.put_metric_data(
    #    Namespace='cloudping',
    #    MetricData=[
    #        {
    #            'MetricName': 'status',
    #            'Dimensions': dimensions,
    #            'Timestamp': timestamp,
    #            'Value': result_value,
    #            'Unit': 'None',
    #            'StorageResolution': 60
    #        },
    #    ]
    #)
    # For cost saving reasons, only send ONE metric. If http status code or contents are not good, don't care about response time!
    if result_value != 0:
        response_time = 999
    client.put_metric_data(
        Namespace='cloudping',
        MetricData=[
            {
                'MetricName': 'responseTime',
                'Dimensions': dimensions,
                'Timestamp': timestamp,
                'Value': response_time,
                'Unit': 'Seconds',
                'StorageResolution': 60
            },
        ]
    )
