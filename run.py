#!flask/bin/python
from app import app
import dotenv

dotenv.load()
app.run(debug=True)
