# SQL · TIER 1 CONCEPTS (INTRODUCTORY)

  <<dim>>Read this once. The first ten questions cover the four verbs below.<</dim>>

  SQL is a language for asking questions of structured data. A relational
  database stores facts in tables, where each row is a record and each column
  is an attribute. Your job at this tier is to pull the right rows and the
  right columns.

# THE FOUR PRIMITIVES

  <<amber>>SELECT<</amber>> picks the columns you want. <<bold>>*<</bold>> grabs all of them.
  <<amber>>FROM<</amber>> names the table. <<amber>>WHERE<</amber>> filters which rows survive.
  <<amber>>ORDER BY<</amber>> sorts the result.

  Every clause is optional except <<amber>>SELECT<</amber>> and <<amber>>FROM<</amber>>. The order
  you write them is fixed: SELECT, FROM, WHERE, ORDER BY. The order the database
  evaluates them is different (FROM first, SELECT last) but that only matters
  later.

# COMPARISONS AND TYPES

  Strings need single quotes. Numbers don't. Booleans live in <<blue>>1<</blue>>/<<blue>>0<</blue>>
  in this dialect. Type mismatches won't error in SQLite, they'll just return
  zero rows, which is the most confusing failure mode in the language.

      <<amber>>WHERE<</amber>> make = <<green>>'Nissan'<</green>>      <<dim>>string<</dim>>
      <<amber>>WHERE<</amber>> year = <<blue>>2020<</blue>>          <<dim>>integer<</dim>>
      <<amber>>WHERE<</amber>> active = <<blue>>1<</blue>>           <<dim>>boolean as int<</dim>>

# COUNTING AND DISTINCT

  <<amber>>COUNT<</amber>>(*) returns the number of rows that survived the filter. It is
  one row of output, regardless of how many rows came in. <<amber>>DISTINCT<</amber>>
  inside <<amber>>SELECT<</amber>> removes duplicate rows from the result.

  <<dim>>Why both exist: COUNT tells you how many, DISTINCT tells you which. Compare<</dim>>
  <<dim>><<qid:sql_intro_04>> (count) with <<qid:sql_intro_07>> (distinct).<</dim>>

  NEXT TIER: AND/OR combinations, BETWEEN, IN, LIKE wildcards, basic aggregates
  beyond COUNT, and conditional bucketing with CASE.

---

# EXAMPLE 1

  Pull every column from a table.

      <<amber>>SELECT<</amber>> * <<amber>>FROM<</amber>> mechanics;

  <<dim>>The <</dim>><<bold>>*<</bold>><<dim>> is shorthand for "all columns in declaration order."<</dim>>
  <<dim>>Useful for exploring; risky in production code because adding a column to the<</dim>>
  <<dim>>table silently changes the query's output shape.<</dim>>

# EXAMPLE 2

  Filter rows by a string match.

      <<amber>>SELECT<</amber>> name, phone
      <<amber>>FROM<</amber>> customers
      <<amber>>WHERE<</amber>> name = <<green>>'Riley Evans'<</green>>;

  <<dim>>Strings are case-sensitive in most dialects. SQLite is loosely typed but<</dim>>
  <<dim>>case-sensitive on equality by default. The fix at the next tier is LOWER().<</dim>>

# EXAMPLE 3

  Sort by a column. This previews the next tier's tooling because real queries
  almost always combine WHERE with sorting and limiting.

      <<amber>>SELECT<</amber>> id, total_cost
      <<amber>>FROM<</amber>> work_orders
      <<amber>>WHERE<</amber>> status = <<green>>'Completed'<</green>>
      <<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>;

  <<dim>>ORDER BY total_cost DESC sorts highest first. At Amateur tier you'll add<</dim>>
  <<dim>>LIMIT to grab just the top N. The two together are how you answer "what are<</dim>>
  <<dim>>the biggest jobs we've ever done." See <</dim>><<qid:sql_am_04>><<dim>>.<</dim>>

