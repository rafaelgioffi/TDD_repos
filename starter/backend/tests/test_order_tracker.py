import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    expected_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
        }
    
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once_with("ORD001", expected_order)


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {
        # "order_id": "ORD_EXISTING"
        "order_id": "ORD001",
        "item_name": "Existing Item",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
        }
    
    with pytest.raises(ValueError, match="Order 'ORD001' already exists."):
        order_tracker.add_order(
            #"ORD_EXISTING", "New Item", 1, "CUST001"
            "ORD001", "New Item", 1, "CUST002"
            )
    # order = order_tracker.get_order_by_id("ORD001")

    # assert order["order_id"] == "ORD001"


def test_get_order_by_id_successfully(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "status": "pending"
    }

    order = order_tracker.get_order_by_id("ORD001")

    assert order["order_id"] == "ORD001"
    

def test_get_order_by_id_inexistent(order_tracker):
    # assert order_tracker.get_order_by_id("INEXISTENT ORDER")
    with pytest.raises(ValueError):
        order_tracker.get_order_by_id("INEXISTENT ORDER")

def test_update_status_successfully(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "status": "pending"
    }
    
    updated_order = order_tracker.update_order_status("ORD001", "completed")
    
    assert updated_order["status"] == "completed"

    mock_storage.save_order.assert_called_once()

def test_update_status_with_inexistent_order(order_tracker):
    with pytest.raises(ValueError):
        order_tracker.update_order_status("INEXISTENT_ORDER", "completed")

def test_list_all_orders(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "status": "pending"
        }
    }

    orders = order_tracker.list_all_orders()
    
    assert orders


def test_list_order_by_status_successfully(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "status": "completed"
        }
    }

    orders = order_tracker.list_orders_by_status("completed")

    assert len(orders) == 1
    assert orders[0]["order_id"] == "ORD001"


def test_list_order_by_status_inexistent(order_tracker):
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status("INEXISTENT_STATUS")
