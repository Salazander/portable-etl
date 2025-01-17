from pyspark.sql import SparkSession
from pyspark.sql import types as T
import pytest
import os
import sys
path = os.path.abspath(os.path.dirname(__file__) + '../../../')
sys.path.append(path)
from common_lib.src.stream_processor import StreamProcessor


@pytest.fixture
def spark():
    return SparkSession.builder.appName("MyPySparkTests").getOrCreate()


def test_stream_processor(spark):
    metadata = spark.read.csv("src/common_lib/tests/rooms.csv", header=True, inferSchema=True)

    test_data = spark.createDataFrame(
        data=['{"deviceId": "sim000001", "deviceTimestamp":"2023-01-01T10:10:11.5091350Z", "doubleValue": 0.2}',
              '{"deviceId": "sim000002", "deviceTimestamp":"2023-01-01T10:10:11.6091350Z", "doubleValue": 0.24}',
              '{"deviceId": "sim000003", "deviceTimestamp":"2023-01-01T10:10:11.6091350Z", "doubleValue": 0.25}'],
        schema=T.StringType()
    )

    dataprocessor = StreamProcessor()
    results = dataprocessor.process_stream(df_metadata=metadata, df_raw_stream=test_data)
    assert [row.roomId for row in results.collect()] == ['room1', 'room1', 'room2']
