# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Simon Fang <sifang@cisco.com> AND Eda Akturk"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from flask import Flask, render_template, request
from dotenv import load_dotenv
import json, os
import requests

load_dotenv()

########################
### Global variables ###
########################

base_url = "https://api.meraki.com/api/v1"
api_key = os.getenv("API_KEY")

selected_organization = []
selected_network = []

app = Flask(__name__)

########################
### Helper Functions ###
########################


def get_header():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }
    print(api_key)
    return headers

def get_organizations():
    url = f"{base_url}/organizations"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def get_networks(organization_id):
    url = f"{base_url}/organizations/{organization_id}/networks"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def get_devices(network_id):
    url = f"{base_url}/networks/{network_id}/devices"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def get_device(network_id, serial):
    url = f"{base_url}/networks/{network_id}/devices/{serial}"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def get_vlan(network_id):
    url = f"{base_url}/networks/{network_id}/appliance/vlans"
    payload = None
    response = requests.request('GET', url, headers=get_header(), data=payload)
    return response.json()


def create_vlan(network_id, vlan, vlan_name, subnet, device_id):
    """
    Create vlan: https://developer.cisco.com/meraki/api-v1/#!create-network-appliance-vlan
    """
    url = f"{base_url}/networks/{network_id}/appliance/vlans"
    payload = {
        "id": vlan,
        "name": vlan_name,
        "subnet": subnet,
        "applianceIp": device_id
    }
    response = requests.request('POST', url, headers=get_header(), data=json.dumps(payload))
    return response.json()


def update_vlan(network_id, vlan, appliance_ip):
    """
    Update network applince vlan: https://developer.cisco.com/meraki/api-v1/#!update-network-appliance-vlan
    """
    url = f"{base_url}/networks/{network_id}/appliance/vlans/{vlan}"
    payload = {
        "applianceIp": appliance_ip
    }
    response = requests.request('PUT', url, headers=get_header(), data=json.dumps(payload))
    return response.json()


def get_config_templates(organization_id):
    """
    Get config templates: https://developer.cisco.com/meraki/api-v1/#!get-organization-config-templates
    """
    url = f"{base_url}/organizations/{organization_id}/configTemplates"
    response = requests.request('GET', url, headers=get_header(), data=None)
    print(response.json())
    return response.json()


def create_config_templates(organization_id, name):
    """
    Create org config template: https://developer.cisco.com/meraki/api-v1/#!create-organization-config-template
    """
    url = f"{base_url}/organizations/{organization_id}/configTemplates"
    payload = {
        "name": name,
        "timeZone": "America/Los_Angeles"
    }

    response = requests.request('POST', url, headers=get_header(), data=json.dumps(payload))
    return response.json()



##############
### Routes ###
##############

# Main page of the app
@app.route('/', methods=['GET'])
def main_page():
    global organizations
    organizations = get_organizations()
    return render_template('columnpage.html', organizations=organizations, selected_organization=selected_organization, selected_network=selected_network)

# step 2 selector
@app.route('/select_organization_network', methods=['POST'])
def select_organization_network():
    global organizations
    global selected_organization
    global selected_network
    global networks
    global devices

    if request.method == 'POST':
        form_data = request.form
        organization_id = form_data['organization_id']

        for organization in organizations:
            if organization_id == organization['id']:
                selected_organization = organization 

        networks = get_networks(organization_id)
        
        if 'network_id' in form_data:
            network_id = form_data['network_id']

            for network in networks:
                if network_id == network['id']:
                    selected_network = network 

            devices = get_devices(network_id)
            templates = get_config_templates(organization_id)

            return render_template('select_device.html', organizations=organizations, networks=networks,
                                   selected_organization=selected_organization,
                                   selected_network=selected_network, devices=devices, templates = templates)

    return render_template('columnpage.html', organizations = organizations, networks = networks, selected_organization = selected_organization,
         selected_network = selected_network)


# config device
@app.route('/config_device', methods=['POST'])
def select_device():
    global organizations
    global selected_organization
    global selected_network
    global networks
    global devices

    if request.method == 'POST':
        form_data = request.form

        if "vlan" in form_data:
            print("****printing the form data ***** ")
            print(form_data)
            print(selected_network)

            vlan = form_data['vlan']
            name = form_data['name']
            subnet = form_data['subnet']
            device_id = form_data['device_id']
            network_id = selected_network['id']

            ## Make the call to create the vlan
            ## create_vlan(network_id, vlan, vlan_name, subnet, device_id)

            message = "vlan created"
            return render_template('config_device.html', organizations=organizations, networks=networks,
                                   selected_organization=selected_organization,
                                   selected_network=selected_network, devices=devices, message=message)

        return render_template('config_device.html', organizations=organizations, networks=networks,
                               selected_organization=selected_organization,
                               selected_network=selected_network, devices=devices)

# apply template
@app.route('/config_template', methods=['POST'])
def config_template():
    global organizations
    global selected_organization
    global selected_network
    global networks
    global devices

    if request.method == 'POST':
        form_data = request.form
        print(form_data)
        if "name" in form_data:
            print(form_data)

            ## Make the api call to create the template

            message = "Created new config template"
            return render_template('config_template.html', organizations=organizations, networks=networks,
                                   selected_organization=selected_organization,
                                   selected_network=selected_network, message=message)

        return render_template('config_template.html', organizations=organizations, networks=networks,
                               selected_organization=selected_organization,
                               selected_network=selected_network)


if __name__ == '__main__':

    app.run()
    #app.run(host='0.0.0.0', port=8080, debug=False)
