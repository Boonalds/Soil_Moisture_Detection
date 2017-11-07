import requests

r = requests.get('https://theia.cnes.fr/atdistrib/services/authenticate/>token.json')

print(r.headers)
print(r.request.headers)
