from datetime import datetime
from collections import defaultdict

def calculate_contract_value(injection_dates, injection_amounts, withdrawal_dates, withdrawal_amounts,
                             injection_prices, withdrawal_prices, injection_rate, withdrawal_rate,
                             max_volume, storage_cost_rate):
    """
    Calculate the net value of a commodity storage contract.

    Args:
        injection_dates (list[datetime]): List of dates for injections.
        injection_amounts (list[float]): List of amounts to inject on each date.
        withdrawal_dates (list[datetime]): List of dates for withdrawals.
        withdrawal_amounts (list[float]): List of amounts to withdraw on each date.
        injection_prices (list[float]): Prices at which the commodity is purchased on injection dates.
        withdrawal_prices (list[float]): Prices at which the commodity is sold on withdrawal dates.
        injection_rate (float): Maximum total amount that can be injected on a single date.
        withdrawal_rate (float): Maximum total amount that can be withdrawn on a single date.
        max_volume (float): Maximum total volume that can be stored.
        storage_cost_rate (float): Storage cost per unit of volume per day.

    Returns:
        float: Net contract value (Withdrawal Revenue - Injection Cost - Storage Cost).
    """
    # Validate input lengths
    if not (len(injection_dates) == len(injection_amounts) == len(injection_prices)):
        raise ValueError("Injection dates, amounts, and prices must have the same length.")
    if not (len(withdrawal_dates) == len(withdrawal_amounts) == len(withdrawal_prices)):
        raise ValueError("Withdrawal dates, amounts, and prices must have the same length.")

    # Aggregate same-day transactions for rate limit checking
    daily_injections = defaultdict(float)
    for d, a in zip(injection_dates, injection_amounts):
        daily_injections[d.date()] += a

    for d, a in daily_injections.items():
        if a > injection_rate:
            raise ValueError(f"Total injection amount {a} on {d} exceeds injection rate {injection_rate}")

    daily_withdrawals = defaultdict(float)
    for d, a in zip(withdrawal_dates, withdrawal_amounts):
        daily_withdrawals[d.date()] += a

    for d, a in daily_withdrawals.items():
        if a > withdrawal_rate:
            raise ValueError(f"Total withdrawal amount {a} on {d} exceeds withdrawal rate {withdrawal_rate}")

    # Combine all events for chronological processing
    events = []
    for d, a, p in zip(injection_dates, injection_amounts, injection_prices):
        events.append({'date': d, 'amount': a, 'price': p, 'type': 'injection'})

    for d, a, p in zip(withdrawal_dates, withdrawal_amounts, withdrawal_prices):
        events.append({'date': d, 'amount': -a, 'price': p, 'type': 'withdrawal'})

    # Sort events by date
    events.sort(key=lambda x: x['date'])

    total_value = 0
    current_inventory = 0
    last_date = None

    for event in events:
        date = event['date']
        amount = event['amount']
        price = event['price']

        # Calculate storage cost from last event to now
        if last_date is not None:
            days = (date - last_date).days
            if days < 0:
                # Should not happen due to sorting, but handle same-day events
                days = 0
            storage_cost = current_inventory * storage_cost_rate * days
            total_value -= storage_cost

        if event['type'] == 'injection':
            # Injection cost
            total_value -= amount * price
            current_inventory += amount
        else: # withdrawal
            # Withdrawal revenue
            # amount is stored as negative for inventory calculation
            withdrawal_qty = -amount
            total_value += withdrawal_qty * price
            current_inventory += amount

        # Check inventory limits
        if current_inventory > max_volume + 1e-9: # tiny epsilon for float precision
            raise ValueError(f"Inventory exceeded max volume: {current_inventory} > {max_volume}")
        if current_inventory < -1e-9:
            raise ValueError(f"Inventory dropped below zero: {current_inventory}")

        last_date = date

    return total_value
