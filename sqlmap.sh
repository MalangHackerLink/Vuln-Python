python sqlmap.py -u "http://127.0.0.1:5000/api/notes/view" --method=POST --headers="Content-Type: application/json\nAuthorization: Bearer ..." --data='{"id": "1"}' -p id --dbs --batch
