# All environment setup and additional decision logic is in README.md

import pandas as pd

# Read all raw data into dataframes
df_cons = pd.read_csv("cons.csv")
df_cons_email = pd.read_csv("cons_email.csv")
df_cons_subscription = pd.read_csv("cons_email_chapter_subscription.csv")

# Remove extraneous columns that will be unused for both people.csv and acquisition_facts.csv.
df_cons_pruned = df_cons[["cons_id", "create_dt", "modified_dt", "create_app", "create_user"]]
df_cons_email_pruned = df_cons_email[df_cons_email["is_primary"] == 1]
df_cons_email_pruned = df_cons_email_pruned[
    ["cons_email_id", "cons_id", "email", "create_dt", "modified_dt", "create_app", "create_user"]
]
df_cons_subscription_pruned = df_cons_subscription[["cons_email_id", "chapter_id", "isunsub", "modified_dt"]]

# First merge email addresses with subscription data to obtain email:sub/unsub correspondence
df = df_cons_email_pruned.merge(df_cons_subscription_pruned, how="left", on="cons_email_id", suffixes=(None, "_subs"))

# Consider emails not present in the subscription table to still be subscribed with chapter_id=1.
df["chapter_id"].fillna(1, inplace=True)
df["isunsub"].fillna(0, inplace=True)
df = df[df["chapter_id"] == 1]

# Merge the pruned email data with the constituent data for additional created/updated data
df = df.merge(df_cons_pruned, on="cons_id", suffixes=(None, "_cons"))

# Cast all date columns to actual datetimes from their default object type
df["create_dt"] = pd.to_datetime(df["create_dt"])
df["modified_dt"] = pd.to_datetime(df["modified_dt"])
df["create_dt_cons"] = pd.to_datetime(df["create_dt_cons"])
df["modified_dt_cons"] = pd.to_datetime(df["modified_dt_cons"])
df["modified_dt_subs"] = pd.to_datetime(df["modified_dt_subs"])

# Use a composite 4-tuple as the 'code' column to avoid losing any creation code data
df["code"] = list(zip(df.create_app, df.create_user, df.create_app_cons, df.create_user_cons))
df["created_dt"] = df[["create_dt", "create_dt_cons"]].min(axis=1)
df["updated_dt"] = df[["modified_dt", "modified_dt_cons", "modified_dt_subs"]].max(axis=1)

# Drop all columns no longer necessary for the end 'people' table
df.drop(columns=["create_app", "create_user", "create_app_cons", "create_user_cons"], inplace=True)
df.drop(columns=["create_dt", "modified_dt", "modified_dt_subs", "create_dt_cons", "modified_dt_cons"], inplace=True)
df.drop(columns=["cons_email_id", "cons_id", "chapter_id"], inplace=True)


acquisition_facts = df.copy(deep=True).drop(columns=["email", "code", "updated_dt"])
acquisition_facts.created_dt = acquisition_facts.created_dt.dt.date  # Cast datetime to date for aggregation purposes
acquisition_facts = acquisition_facts.groupby(["created_dt"]).size()
acquisition_facts = acquisition_facts.to_frame().rename(columns={"created_dt": "acquisition_date", 0: "acquisitions"})

# Export both tables to CSVs in the working directory
df.to_csv("people.csv")
acquisition_facts.to_csv("acquisition_facts.csv")
