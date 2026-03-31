from datetime import datetime
from commodity_pricing import calculate_contract_value

def run_tests():
    # Case 1: Simple Buy Low, Sell High
    print("Running Case 1: Simple seasonal buy-sell...")
    injection_dates = [datetime(2023, 6, 1)]
    injection_amounts = [1000]
    injection_prices = [2.0]
    withdrawal_dates = [datetime(2023, 12, 1)]
    withdrawal_amounts = [1000]
    withdrawal_prices = [5.0]

    # Costs & constraints
    injection_rate = 1000
    withdrawal_rate = 1000
    max_volume = 1000
    storage_cost_rate = 0.01 # per unit per day

    val = calculate_contract_value(
        injection_dates, injection_amounts, withdrawal_dates, withdrawal_amounts,
        injection_prices, withdrawal_prices, injection_rate, withdrawal_rate,
        max_volume, storage_cost_rate
    )
    print(f"Contract value: {val}")

    # Case 2: Multiple injections and withdrawals
    print("\nRunning Case 2: Multiple events...")
    injection_dates = [datetime(2023, 6, 1), datetime(2023, 7, 1)]
    injection_amounts = [500, 500]
    injection_prices = [2.0, 2.5]
    withdrawal_dates = [datetime(2023, 11, 1), datetime(2023, 12, 1)]
    withdrawal_amounts = [500, 500]
    withdrawal_prices = [4.5, 5.0]

    val = calculate_contract_value(
        injection_dates, injection_amounts, withdrawal_dates, withdrawal_amounts,
        injection_prices, withdrawal_prices, injection_rate, withdrawal_rate,
        max_volume, storage_cost_rate
    )
    print(f"Contract value: {val}")

    # Case 3: Test rate limit violation
    print("\nRunning Case 3: Test injection rate violation...")
    try:
        calculate_contract_value(
            [datetime(2023, 1, 1)], [2000], [], [], [1.0], [],
            injection_rate=1000, withdrawal_rate=1000, max_volume=2000, storage_cost_rate=0.01
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Case 4: Test capacity limit violation
    print("\nRunning Case 4: Test max volume violation...")
    try:
        calculate_contract_value(
            [datetime(2023, 1, 1), datetime(2023, 1, 2)], [1000, 1000], [], [], [2.0, 2.0], [],
            injection_rate=1000, withdrawal_rate=1000, max_volume=1500, storage_cost_rate=0.01
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Case 5: Test same-day transaction aggregation
    print("\nRunning Case 5: Test same-day aggregation for rate limit violation...")
    try:
        calculate_contract_value(
            [datetime(2023, 1, 1, 10, 0), datetime(2023, 1, 1, 14, 0)], [600, 600], [], [], [2.0, 2.0], [],
            injection_rate=1000, withdrawal_rate=1000, max_volume=2000, storage_cost_rate=0.01
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Case 6: Input length validation
    print("\nRunning Case 6: Input length validation...")
    try:
        calculate_contract_value(
            [datetime(2023, 1, 1)], [1000, 1000], [], [], [1.0], [],
            1000, 1000, 2000, 0.01
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    run_tests()
