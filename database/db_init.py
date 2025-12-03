from db import engine, Base
from db import Ticket  # import your model

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
