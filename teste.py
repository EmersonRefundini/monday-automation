import requests

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYzNDE4NzM5NiwiYWFpIjoxMSwidWlkIjoyMjU5MTk4NCwiaWFkIjoiMjAyNi0wMy0xN1QxNDozMjo0Ny4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjA0MjUzOSwicmduIjoidXNlMSJ9.M2cgYDiMVPEo9mLSe096pjY0Vw-_s_jv9rxl0MOA5Ug"

url = "https://api.monday.com/v2"

query = {
    "query": "{ me { name } }"
}

headers = {
    "Authorization": API_KEY
}

response = requests.post(url, json=query, headers=headers)

print(response.json())