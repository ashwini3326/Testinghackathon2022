import pandas as pd
import pytest
import logging

# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


@pytest.mark.parametrize(
    "sourceFile,targetFile",
    [
        ("Sales_mysql.csv", "Sales_sql.csv"),
    ],
)
class validateData:
    df_source = pd.read_csv(sourceFile)
    df_target = pd.read_csv(targetFile)

    def test_shapeValidation(self.df_source:pd.core.frame.DataFrame, self.df_target:pd.core.frame.DataFrame) -> None:

        shape =  self.df_source.shape == self.df_target.shape
        logger.info(shape)
        assert False not in list(shape)

        columnsValidation = self.df_source.columns == df_target.columns
        logger.info(columnsValidation)
        assert False not in list(columnsValidation)

    def test_schemaValidation(df_source:pd.core.frame.DataFrame, df_target:pd.core.frame.DataFrame) -> None:
        schemaValidation = df_source.dtypes == df_target.dtypes
        logger.info(schemaValidation)


    def test_countValidation(df_source:pd.core.frame.DataFrame, df_target:pd.core.frame.DataFrame) -> None:
        countDataFrame = pd.concat([df_source.count(),df_target.count()], axis=1)
        countDataFrame["matching"] = countDataFrame[0] == countDataFrame[1]


"""
def validateData(df_source:pd.core.frame.DataFrame, df_target:pd.core.frame.DataFrame) -> list[bool]:
    
    validationResult:List = [result for result in [
        validation1(df_source, df_target),
        validation2(df_source, df_target),
    ]]
    
    return validationResult
"""
