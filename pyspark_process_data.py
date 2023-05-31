import argparse

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructType

# create spark session
spark = SparkSession.builder.appName("PySparkApp").getOrCreate()

# create schema
schema = (
    StructType()
    .add("marketplace", StringType(), True)
    .add("customer_id", StringType(), True)
    .add("review_id", StringType(), True)
    .add("product_id", StringType(), True)
    .add("product_parent", IntegerType(), True)
    .add("product_title", StringType(), True)
    .add("product_category", StringType(), True)
    .add("star_rating", IntegerType(), True)
    .add("helpful_vote", IntegerType(), True)
    .add("total_vote", IntegerType(), True)
    .add("vine", StringType(), True)
    .add("verified_purchase", StringType(), True)
    .add("review_headline", StringType(), True)
    .add("review_body", StringType(), True)
    .add("myyear", StringType(), True)
)


def main():
    """
    parse argument
    """
    # define parser
    parser = argparse.ArgumentParser(description="app inputs and outputs")
    parser.add_argument("--source_bucket_name", type=str, help="s3 input bucket")
    parser.add_argument("--dest_bucket_name", type=str, help="output s3 prefix")

    # parse argument
    args = parser.parse_args()
    print(f"{args.source_bucket_name} and {args.dest_bucket_name}")

    # read data from s3
    df_csv = (
        spark.read.format("csv")
        .option("header", True)
        .schema(schema)
        .option("delimiter", "\t")
        .option("quote", '"')
        .load(f"s3://{args.source_bucket_name}/tsv/")
    )

    # transform and feature engineer
    df_clean = df_csv.where("marketplace='US'").select(
        "marketplace", "customer_id", "product_id", "star_rating"
    )

    # write data to s3
    df_clean.write.format("parquet").save(
        f"s3://{args.dest_bucket_name}/amazon-reviews/"
    )


if __name__ == "__main__":
    main()