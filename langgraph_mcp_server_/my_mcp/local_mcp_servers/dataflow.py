import os
import subprocess
from typing import Optional
import pandas as pd
import duckdb
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()
mcp = FastMCP("dataflow")


class DataFlowSession:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.working_dir = os.environ.get("MCP_FILESYS_DIR", None)

    async def load_data(self, file_path: str) -> str:
        try:
            self.data = pd.read_csv(file_path)
            return f"Data loaded from {file_path}"
        except (pd.errors.ParserError, FileNotFoundError) as e:
            return f"Error loading data: {str(e)}"

    async def query_data(self, query: str) -> str:
        if self.data is None:
            return "Error, no data loaded."
        try:
            con = duckdb.connect(database=':memory:')
            con.register('data', self.data)
            result = con.execute(query).fetchdf()
            return result.to_string()
        except (duckdb.Error, KeyError, ValueError) as e:
            return f"Error executing query: {str(e)}"

    async def create_new_directory(self, dir_name: str) -> str:
        try:
            dir_ = self.working_dir+"/"+dir_name
            if os.path.exists(dir_):
                raise ValueError(f"Directory {dir_} already exists.")
            os.mkdir(dir_)
            os.chdir(dir_)
            subprocess.run(['echo', '"Hello World!"', '>', 'README.md'],
                           check=True)
            return f"Directory {dir_} created."
        except OSError as e:
            return f"Error creating folder: {str(e)}"


session = DataFlowSession()


@mcp.tool()
async def dataflow_load_data(file_path: str) -> str:
    """
    Load data from a file into the session.

    Args:
        file_path: The absolute path the file
    """
    return await session.load_data(file_path)


@mcp.tool()
async def dataflow_query_data(sql_query: str) -> str:
    """
    Query the loaded data. Data must first be loaded using the
    dataflow_load_data tool, data is located in table 'data'.

    Args:
        sql_query: A valid SQL query.
    """
    return await session.query_data(sql_query)


@mcp.tool()
async def dataflow_create_new_directory(dir_name: str) -> str:
    """
    Create a new directory with directory name given by parameter.

    Args:
        dir_name: A valid directory name.
    """
    return await session.create_new_directory(dir_name)


if __name__ == "__name__":
    mcp.run(transport='stdio')
