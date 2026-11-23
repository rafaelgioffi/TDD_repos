from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json()

    try:
        status_order = order_tracker.add_order(
            order_id=data.get('order_id'),
            item_name=data.get('item_name'), 
            quantity=data.get('quantity'),
            customer_id=data.get('customer_id'),
            status=data.get('status', 'pending')
            )
    except ValueError as error:
        return jsonify({"Add Order Error": str(error)}), 400
        
    return jsonify({"message": "Order added successfully", "order_id": request.json.get('order_id')}), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
   
    return jsonify(order), 200


@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json()
    new_status = data.get('new_status')

    try:
        updated_order = order_tracker.update_order_status(order_id, new_status)
    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    return jsonify(updated_order), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    try:
        status_filter = request.args.get('status')
        if status_filter:
            orders = order_tracker.list_orders_by_status(status_filter)
        else:
            orders = order_tracker.list_all_orders()
    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    return jsonify(orders), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
