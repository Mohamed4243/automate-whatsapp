
import ssl
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

# database connection
cluster = MongoClient("mongodb+srv://bashi:4243bb@cluster0.vt2qy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# # dbname
db = cluster['bakery']
# users table
users = db['users']
#orders table
orders = db['orders']
app =Flask(__name__)

@app.route("/", methods=["get","post"])
def repy():
    text = request.form.get("Body")
    number = request.form.get("From")
    # removing whatsApp 
    number = number.replace("whatsapp:","")

    response = MessagingResponse()
    # msg = response.message(f"Thanks for contacting me you have sent '{text}' from {number}")
    # msg.media("https://images.unsplash.com/photo-1616879577377-ca82803b8c8c?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1374&q=80")
    user = users.find_one({"number": number})
    if bool(user) == False:
        response.message("""Hi, thanks for contacting *the bakal bakery*\nYou can choose from one of the options below.\n\n*Type*\n\n1️⃣ to *contact* us\n2️⃣ to *order* snacks\n3️⃣ to know our *working hours*\n4️⃣ to get *address*
                 """)
        users.insert_one({"number":number, "status": "main","messages":[]})
    elif user['status'] =='main':
      
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)

        if option == 1:
            response.message("You can *contact* us: 0617558833\nEmail: msg@gmail.com")
        elif option == 2:
            response.message("You have entered *ordering mode*")
            users.update_one({"number":number},{"$set":{"status": "ordering"}})
            response.message("You can select one of the following cakes\n\n1️⃣ Ice cream\n2️⃣ Plum cake\n3️⃣ Carrot cake\n0️⃣Go back")
        elif option ==3:
            response.message("We work from *9:00pm* to *12:00am*")
        elif option==4: 
            response.message("Address:Tree Piano, Maka Al Mukarama Road, Muqdisho")
        else:
            response.message("Please enter valid response")
            
    elif user['status'] =="ordering":
        try:
            option = int(text)
        except:
            response.message("Please enter valid response")
            return str(response)
       
        if option ==0:
              users.update_one({"number":number},{"$set":{"status": "main"}})
              response.message("""Hi, thanks for contacting *the bakal bakery*\nYou can choose from one of the options below.\n\n*Type*\n\n1️⃣ to *contact* us\n2️⃣ to *order* snacks\n3️⃣ to know our *working hours*\n4️⃣ to get *address*
                 """)
        elif 1 <= option <= 9:
            cakes=["Ice cream","Plum cake","Carrot cake"]
            selectedCakes = cakes[option -1]
            users.update_one({"number":number},{"$set":{"status": "address"}})
            users.update_one({"number":number},{"$set":{"item": selectedCakes}})
            response.message("Good choice! 😊")
            response.message("Please enter your address to confirm the order")
        else:
            response.message("Please enter valid response")
    elif user['status'] == "address":
        selected = user['item']
        response.message("Thanks for shopping with us")
        response.message(f"Your order *{selected}* has been received and you will get within an hour ")
        orders.insert_one({"number":number, "item": selected,"address": text,"order_date": datetime.now()})
        users.update_one({"number":number},{"$set":{"status": 'ordered'}})
    elif user["status"] == "ordered":
         response.message("""Hi, thanks for contacting us again *the bakal bakery*\nYou can choose from one of the options below.\n\n*Type*\n\n1️⃣ to *contact* us\n2️⃣ to *order* snacks\n3️⃣ to know our *working hours*\n4️⃣ to get *address*
                 """)
         users.update_one({"number":number},{"$set":{"status": 'main'}})
    users.update_one({"number": number}, {"$push": {"messages":{"text":text,"date":datetime.now()}}})
    return str(response)


if __name__ =="__main__":
    app.run()
