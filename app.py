import logging
from logging.config import dictConfig

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, Ticket

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usertickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)
CORS(app)


class AllTickets(Resource):

    def get(self):
        response_dict_list = [n.to_dict() for n in Ticket.query.all()]
        response = make_response(
            response_dict_list,
            200,
        )
        return response


    def post(self):
        data = request.get_json()
        logging.info(f'Incoming ticket create data: {data}')
        try:
            new_ticket = Ticket(
                title=data['title'],
                created_by=data['created_by'],
                description=data['description'],
            )
        except ValueError as e:
            return make_response({"error": str(e)}, 400)

        db.session.add(new_ticket)
        db.session.commit()
        self.notify_admin_of_ticket_create(new_ticket)
        response_dict = new_ticket.to_dict()
        response = make_response(
            response_dict,
            201,
        )
        return response

    def notify_admin_of_ticket_create(self, ticket):
        logging.info(
            'Would normally send email here with body:' +
            '\n A new ticket has been created.' +
            f'\n Title:{ticket.title}' +
            f'\n Created By:{ticket.created_by}' +
            f'\n Description:{ticket.description}'
            '\n Please respond to this ticket at your earliest convenience.'
        )


api.add_resource(AllTickets,'/tickets')


class TicketById(Resource):
    def get(self, id):
        response_dict = Ticket.query.filter_by(id=id).first().to_dict()
        response = make_response(
            response_dict,
            200,
        )
        return response

    def patch(self, id):
        record = Ticket.query.filter(Ticket.id == id).first()
        data = request.get_json()
        logging.info(f'Incoming ticket update data: {data}')

        if data.get('status'):
            record.status = data['status']

        if data.get('response'):
            record.response = data['response']

        db.session.add(record)
        db.session.commit()

        self.notify_user_of_ticket_update(record)

        response_dict = record.to_dict()
        response = make_response(
            response_dict,
            200
        )

        return response

    def delete(self, id): 
        ticket = Ticket.query.get(id)

        if ticket:
            db.session.delete(ticket)
            db.session.commit()
            return make_response({"Ticket deleted successfully"}, 200)
        else:
            return make_response({"error": "Ticket not found"}, 404)

    def notify_user_of_ticket_update(self, ticket):
        logging.info(
            'Would normally send email here with body:' +
            '\n Your ticket has been updated.' +
            f'\n Title:{ticket.title}' +
            f'\n Description:{ticket.description}' +
            f'\n Response:{ticket.response}' +
            f'\n Status:{ticket.status}' +
            '\n Please review the ticket and respond if necessary.'
        )

api.add_resource(TicketById, '/tickets/<int:id>')

if __name__ == '__main__':
    app.run(port=5000)




