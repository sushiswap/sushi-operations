import os

from utils.gas import gas_price_mainnet, gas_price_arbitrum

# Retrieve job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
# Retrieve user-defined env vars
MAINNET_RPC_URL = os.getenv("MAINNET_RPC_URL", "")


def main():
  print("Running MiniChef Servers Job")
  print(f"Starting Task #{TASK_INDEX}, Atempt #{TASK_ATTEMPT}...")
  test_gas = gas_price_mainnet()
  test_gas_arbi = gas_price_arbitrum()

  print("Gas Prices are:")
  print(test_gas)
  print(test_gas_arbi)

  print(f"Completed Task #{TASK_INDEX}.")



if __name__ == "__main__":
  try:
    main()
  except Exception as err:
    message = f"Task #{TASK_INDEX}, " \
      + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
    print(json.dumps({"message": message, "severity": "ERROR"}))
    sys.exit(1)  # Retry Job Task by exiting the process
