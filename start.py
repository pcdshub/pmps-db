import argparse

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from base import Session, engine, Base
# Models need to be imported for base to know what tables to create
from models import devices, history, states, device_states
def main(args):
    if args.reset:
        answer = input("CAUTION: this will delete all tables.\nContinue? (Y/N): ")
        if answer.upper() in ["Y", "YES"]:
            delete_db()
        elif answer.upper() == ["N", "NO"]:
            print("Exiting.")
            return
        else:
            print("Unclear Input. Exiting.")
            return
    #db_url = "sqlite:///{path_to_db}".format(path_to_db=db_path)
    create_tables()
    #delete_db()
    return

def create_tables():
    """
    Creates all tables to be used in the pmps database.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except:
        print("ERROR: Unable to create initial tables.")
        return
    print("Tables Created")
    return

def delete_db():
    """
    Deletes all data in tables in the pmps database. 
    """
    #Add function to delete all tables/rows
    try:
        Base.metadata.drop_all(engine)
    except exc.OperationalError as e:
        print("ERROR: Database does not exist, cannot delete tables.")
        return
    print("Tables Deleted")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Various start up tasks')
    parser.add_argument('-r',  '--reset', action='store_true', required=False,
        help='delete all data and recreate fresh tables')
    parser.add_argument('-c', '--create', action='store_true', required=False,
        help='create a fresh set of tables')
    args = parser.parse_args()
    main(args)
