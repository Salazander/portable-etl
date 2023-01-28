from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    DoubleType
)


class StreamProcessor:
    def __init__(self) -> None:
        self.stream_schema = StructType([
            StructField("deviceId", StringType()),
            StructField("time", TimestampType()),
            StructField("doubleValue", DoubleType())
        ])

    def process_stream(self, df_metadata: DataFrame,
                       df_raw_stream: DataFrame) -> DataFrame:
        df_output_stream = (df_raw_stream
                            .selectExpr("CAST(value AS STRING)")
                            .select(F.from_json(F.col("value"),
                                    self.stream_schema).alias("data"))
                            .select("data.*"))

        windowSpec = F.window("time", "5 seconds")

        # Watermarking handles late arrivals
        # https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#handling-late-data-and-watermarking
        return (df_output_stream
                .withWatermark("time", "5 seconds")
                .groupBy(windowSpec, "deviceId")
                .agg(F.avg("doubleValue").alias("avgValue"))
                .join(df_metadata, on="deviceId")
                .selectExpr("deviceId", "roomId", "avgValue",
                            "window.start as start", "window.end as end"))
