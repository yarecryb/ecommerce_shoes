# Example workflow
1. User registers by sending their details to `POST /users/create_users`.

# Testing results
<Repeated for each step of the workflow>

curl -X 'POST' \
  'https://ecommerce-shoes-vz56.onrender.com/users/create_users' \
  -H 'accept: application/json'
[
    {
    "full_name": "someoneelse",
    "email": "idk",
    "password": "10",
    "username": "someonelese"
    }
]

"User(s) created!"