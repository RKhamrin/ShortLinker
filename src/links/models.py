from sqlalchemy import Table, Column, Integer, DateTime, MetaData, String, Boolean
metadata = MetaData()

linking = Table(
    "links",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("long_link", String, nullable=False),
    Column("custom_alias", String, nullable=False),
    Column("expires_at", DateTime, nullable=False),
    Column("last_usage", DateTime, nullable=False),
    Column("creation_date", DateTime, nullable=False),
    Column("number_of_usages", Integer, nullable=False),
    Column("is_authorized", Boolean, nullable=False)
)
