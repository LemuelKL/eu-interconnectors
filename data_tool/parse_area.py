import pandas as pd


# Add quote after the first comma of each line
with open("area_raw.csv", "r") as f:
    lines = f.readlines()

    lines = [line.replace(",", ",'", 1) for line in lines]

    lines = [line.replace("\n", "'\n") for line in lines]


with open("area_raw.csv", "w") as f:
    f.writelines(lines)

df = pd.read_csv("area_raw.csv", quotechar="'")
print(df)

# Create an empty DataFrame to store the associations
result_df = pd.DataFrame(columns=["Key", "Code"])

# Iterate through each row and split the 'Meaning' values
for _, row in df.iterrows():
    meanings = row["Meaning"].split(", ")
    code = row["Code"]
    for meaning in meanings:
        result_df = pd.concat(
            [result_df, pd.DataFrame([[meaning, code]], columns=["Key", "Code"])],
            ignore_index=True,
        )

print(result_df)
result_df.to_csv("area.csv", index=False)

