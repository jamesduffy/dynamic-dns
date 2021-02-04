import CloudFlare
import tldextract

from flask import Flask, request, abort
from marshmallow import Schema, fields, ValidationError


app = Flask(__name__)


class DnsUpdateSchema(Schema):
    username = fields.Email(required=True)
    password = fields.Str(required=True)
    hostname = fields.Str(required=True)
    ip_address = fields.IP(required=True)


@app.route('/update')
def update():
    try:
        data = DnsUpdateSchema().load(request.args)
    except ValidationError as err:
        return err

    cf = CloudFlare.CloudFlare(email=data['username'], token=data['password'])

    # Split hostname into parts to get zone name for cloudflare
    domain = tldextract.extract(data['hostname'])

    zone_name = f"{domain.domain}.{domain.suffix}"
    subdomain = domain.subdomain

    try:
        zones = cf.zones.get(params={'name': zone_name})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        return {'status': 'error', 'message': 'cloudflare authentication failed or unknown'}

    # Test that only one zone was returned
    if len(zones) == 0:
         return {'status': 'error', 'message': f'cloudflare zone {zone_name} not found'}

    if len(zones) != 1:
        return {'status': 'error', 'message': f'cloudflare returned {len(zones)} zones'}


    zone = zones[0]
    zone_name = zone['name']
    zone_id = zone['id']
    ip_address = str(data['ip_address'])

    try:
        params = {'name': data['hostname'], 'match': 'all'}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records %s - %d %s - api call failed' % (dns_name, e, e))

    updated = False

    # update the record - unless it's already correct
    for dns_record in dns_records:
        old_ip_address = dns_record['content']

        if ip_address == old_ip_address:
            return {
                'status': 'ok',
                'message': f'update not required for record {subdomain}.{zone_name} already pointed to {ip_address}'
            }

        # Yes, we need to update this record - we know it's the same address type
        dns_record_id = dns_record['id']
        dns_record = {
            'name': subdomain,
            'type': 'A',
            'content': ip_address,
            'proxied': dns_record['proxied']
        }
        try:
            dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            return {'status': 'error', 'message': 'cloudflare update dns record call failed'}
        updated = True

    if updated:
        return {
            'status': 'ok',
            'message': f'updated record {subdomain}.{zone_name} to {ip_address}'
        }

    # No existing dns record to update - so create dns record
    dns_record = {
        'name': subdomain,
        'type': 'A',
        'content': ip_address,
    }
    try:
        dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        return {'status': 'error', 'message': 'cloudflare create dns record call failed'}
    return {
        'status': 'ok',
        'message': f'created record {subdomain}.{zone_name} to {ip_address}'
    }
