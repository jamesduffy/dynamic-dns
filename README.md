# Dynamic DNS
This is a simple python Flask app that you can setup with your Synology or compatible system to set a dynamic DNS record in Cloudflare. 

I used this for a short period mainly as a proof of concept, but decided to use an [alternative method detailed on my website](https://duffy.xyz/2021/custom-synology-dynamic-dns/#option-2-setup-a-cname).

# Usage
1. Setup this Flask app running in the cloud somewhere. It has to be setup outside your network to be accessible to when your IP changes.
2. Setup the custom DDNS provider in your Synology Control Panel under External Access > DDNS > Customize
   - The query URL will be something like this:
     ```https://ddns.example.com/update?hostname=__HOSTNAME__&ip_address=__MYIP__&password=__PASSWORD__&username=__USERNAME__```
3. Add the custom DDNS provider:
   - Select your custom provider from the dropdown
   - Hostname: The hostname you want to dynamically update
   - Username/Email: The email associated with your Cloudflare Account
   - Password/Key: The API token from your Cloudflare Account
