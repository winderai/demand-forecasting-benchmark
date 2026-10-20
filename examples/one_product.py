import pandas as pd
from timestral import TimestralForecaster

weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
sales = weekly[weekly["unique_id"] == "85123A"].set_index("ds")["y"]  # white hanging heart T-light holder
history = sales[:"2011-10-09"]

model = TimestralForecaster.from_pretrained("mistralai/Timestral-209M")
forecast = model.forecast(history.to_numpy(), prediction_length=8)

print(pd.DataFrame({
    "p10": forecast.quantile(0.1)[0, 0].numpy(), "median": forecast.median[0, 0].numpy(),
    "p90": forecast.quantile(0.9)[0, 0].numpy(), "actual": sales["2011-10-16":][:8].to_numpy(),
}, index=sales["2011-10-16":][:8].index).round(0))
