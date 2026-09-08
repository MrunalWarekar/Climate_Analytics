from utils.data_manager import DataManager


manager = DataManager()

manager.load_dataset(
    "Environment_Temperature_change_E_All_Data_NOFLAG.csv"
)

print("\n========== DATASET ==========")
print("Rows:", manager.metadata["rows"])
print("Columns:", manager.metadata["columns"])

print("\n========== OPTIONS ==========")

print("Countries/Areas:",
      len(manager.areas))

print("First 10 areas:",
      manager.areas[:10])

print("Measurements:",
      manager.elements)

print("Months:",
      manager.months)

print("\n========== YEARS ==========")

print("First year:",
      manager.metadata["first_year"])

print("Last year:",
      manager.metadata["last_year"])

print("Number of year columns:",
      len(manager.year_columns))


print("\n========== ANALYTICAL DATA ==========")

df = manager.create_analytical_dataset(
    area="India",
    element="Temperature change",
    month="January",
    start_year=1990,
    end_year=2019
)

print(df.head())

print("\nRows:", len(df))

print("\nColumns:",
      df.columns.tolist())

print("\nYear range:",
      df["YEAR"].min(),
      "to",
      df["YEAR"].max())

print("\n========== SUCCESS ==========")