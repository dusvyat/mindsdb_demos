import sqlite3
import mysql.connector
import pandas as pd
from mindsdb_sql import parse_sql


class SqliteHelper:

	def __init__(self, db_name):

		self.conn = sqlite3.connect(db_name)
		self.cursor = self.conn.cursor()

	def __enter__(self):

		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):

		self.conn.commit()
		self.conn.close()

		return True

	def create_table_from_csv_or_df(self, data, table_name):

		if isinstance(data, str):

			(
				pd.read_csv(data, sep=",", header=0)
				.to_sql(table_name, con=self.conn, if_exists="replace")
			)

		elif isinstance(data, pd.DataFrame):

			(
				data
				.to_sql(table_name, con=self.conn, if_exists="replace")
			)

		else:
			raise ValueError("'data_type' must be csv or df")

	def read_data_from_db(self, table_name):

		df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)

		return df

	def create_tables(self, data: list[dict]) -> None:
		# create tables from csv or df

		for _data in data:
			self.create_table_from_csv_or_df(**_data)


class MySqlHelper:

	def __init__(self, host, user, port):
		self.conn = mysql.connector.connect(
			host=host,
			user=user,
			port=port,
		)
		self.cursor = self.conn.cursor()

	def __enter__(self):
		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.conn.commit()
		self.conn.close()
		return True

	def create_sqlite_db(self, db_name, db_file_path):
		parameters = {"db_file": f'{db_file_path}'}
		query = f"CREATE DATABASE {db_name} WITH ENGINE='sqlite', PARAMETERS={parameters};"

		self.cursor.execute(parse_sql(query, dialect="mindsdb"))

	def create_recommender_query(self, **kwargs):
		query = """
		CREATE MODEL {model_name} FROM {integration_name} (select * from {input_table_name}) 
		predict {item_id}
			using
				engine='lightfm',
				item_id='{item_id}',
				user_id='{user_id}',
				threshold={threshold},
				recommendation_type='{recommendation_type}',
				n_recommendations={n_recommendations};
				""".format(**kwargs)

		return parse_sql(query, dialect="mindsdb")

	def create_qa_query(self, **kwargs):
		query = """
		CREATE MODEL {model_name}
		FROM {integration_name} (select * from {input_table_name}) 
		PREDICT answer
		USING 
			engine = 'writer',
			model_name = '{model_name}',
			organisation = '{organisation_id}',
			api_key = '{api_key}',
			prompt_template = '{question}';
			""".format(**kwargs)

		return parse_sql(query, dialect="mindsdb")

	def query(self, query):
		self.cursor.execute(parse_sql(query, dialect="mindsdb"))
		return self.cursor.fetchall()


def run(sqlite_db: str,data: list[dict]) -> None:
	sqlite_helper = SqliteHelper(sqlite_db)

	# create tables from csv or df

	for _data in data:
		sqlite_helper.create_table_from_csv_or_df(**_data)


