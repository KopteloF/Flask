import requests
#
response = requests.post('http://127.0.0.1:5000/api',
                         json={
                             'article': 'valideted art',
                             'description': 'some discription',
                             'owner': 'Host'
                         })

# response = requests.get('http://127.0.0.1:5000/api/4')

# response = requests.patch('http://127.0.0.1:5000/api/13',
#                          json={
#                              'article': 'Fixed header',
#                              'description': 'FINE',
#                              'owner': 'Host'
#                          })

# # #
# response = requests.delete('http://127.0.0.1:5000/api/14')
print(response.text)
