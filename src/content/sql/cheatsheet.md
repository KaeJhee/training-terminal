# SQL CHEATSHEET

  <<dim>>A working reference for the whole language. Skim it once, come back when stuck.<</dim>>

# SELECT AND PROJECTION

  <<amber>>SELECT<</amber>> picks columns out of a table. <<bold>>*<</bold>> grabs every column;
  naming columns is better practice because the query keeps working when the
  schema changes.

      <<amber>>SELECT<</amber>> name, phone <<amber>>FROM<</amber>> customers;
      <<amber>>SELECT<</amber>> <<amber>>DISTINCT<</amber>> make <<amber>>FROM<</amber>> vehicles;

  <<dim>>Aliases rename a column or expression in the result. See <<qid:sql_am_10>>.<</dim>>

      <<amber>>SELECT<</amber>> total_cost <<amber>>AS<</amber>> cost_usd <<amber>>FROM<</amber>> work_orders;

# WHERE: FILTERING ROWS

  Predicates filter rows before any aggregation or grouping happens. Combine
  with <<amber>>AND<</amber>> / <<amber>>OR<</amber>>. Strings go in single quotes.

      <<amber>>WHERE<</amber>> make = <<green>>'Nissan'<</green>> <<amber>>AND<</amber>> year <<amber>>BETWEEN<</amber>> <<blue>>1990<</blue>> <<amber>>AND<</amber>> <<blue>>1999<</blue>>
      <<amber>>WHERE<</amber>> status <<amber>>IN<</amber>> (<<green>>'Open'<</green>>, <<green>>'In Progress'<</green>>)
      <<amber>>WHERE<</amber>> name <<amber>>LIKE<</amber>> <<green>>'K%'<</green>>

  <<red>>NULL is not equal to anything<</red>>, not even itself. Use <<amber>>IS NULL<</amber>>
  and <<amber>>IS NOT NULL<</amber>>, never <<amber>>= NULL<</amber>>.

# AGGREGATION

  Aggregates collapse many rows into one. Bare aggregates over the whole table
  produce one row. With <<amber>>GROUP BY<</amber>> you get one row per group.

      <<amber>>SELECT<</amber>> <<amber>>COUNT<</amber>>(*), <<amber>>AVG<</amber>>(total_cost), <<amber>>SUM<</amber>>(total_cost) <<amber>>FROM<</amber>> work_orders;
      <<amber>>SELECT<</amber>> status, <<amber>>COUNT<</amber>>(*) <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> status;

  <<amber>>HAVING<</amber>> filters groups after aggregation. <<amber>>WHERE<</amber>> filters rows
  before. Use the right one or you will count things twice.

      <<amber>>GROUP BY<</amber>> customer_id <<amber>>HAVING<</amber>> <<amber>>COUNT<</amber>>(*) >= <<blue>>2<</blue>>

# JOINS

  A join walks two tables side by side, matching rows on a shared key. Inner
  join keeps only matched rows. <<amber>>LEFT JOIN<</amber>> keeps every row from the left
  table even when the right has no match.

      <<amber>>SELECT<</amber>> c.name, v.make
      <<amber>>FROM<</amber>> customers c
      <<amber>>JOIN<</amber>> vehicles v <<amber>>ON<</amber>> v.customer_id = c.id;

  <<dim>>Three tables chain the same way. See <<qid:sql_int_09>>.<</dim>>

# CASE EXPRESSIONS

  <<amber>>CASE<</amber>> is SQL's if/else. Use it to bucket continuous values, or to count
  conditional matches inside an aggregate (the pivot trick).

      <<amber>>CASE<</amber>> <<amber>>WHEN<</amber>> total_cost >= <<blue>>2000<</blue>> <<amber>>THEN<</amber>> <<green>>'High'<</green>> <<amber>>ELSE<</amber>> <<green>>'Low'<</green>> <<amber>>END<</amber>>

# WINDOW FUNCTIONS

  Window functions compute a value per row using a frame of related rows.
  Unlike <<amber>>GROUP BY<</amber>>, the original rows are preserved.

      <<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> revenue <<amber>>DESC<</amber>>)
      <<purple>>ROW_NUMBER<</purple>>() <<amber>>OVER<</amber>> (<<amber>>PARTITION BY<</amber>> status <<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>)
      <<purple>>SUM<</purple>>(total_cost) <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> id) <<amber>>AS<</amber>> running_total

# CTEs AND SUBQUERIES

  A common table expression is a named query you can reuse downstream. Easier
  to read than nested subqueries when the logic has steps.

      <<amber>>WITH<</amber>> rev <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> mechanic_id, <<amber>>SUM<</amber>>(total_cost) <<amber>>AS<</amber>> revenue
          <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> mechanic_id
      )
      <<amber>>SELECT<</amber>> * <<amber>>FROM<</amber>> rev <<amber>>WHERE<</amber>> revenue > <<blue>>5000<</blue>>;

  <<purple>>WITH RECURSIVE<</purple>> generates sequences or walks hierarchies. The base
  case unions to itself with a guard.

# QUALITY-OF-LIFE

  <<amber>>COALESCE<</amber>>(col, <<green>>'fallback'<</green>>) replaces NULLs. <<amber>>ROUND<</amber>>(x, <<blue>>2<</blue>>)
  trims float noise. <<amber>>LOWER<</amber>>/<<amber>>UPPER<</amber>> normalize case before LIKE
  comparisons. <<amber>>ORDER BY<</amber>> x <<amber>>DESC<</amber>> <<amber>>LIMIT<</amber>> <<blue>>N<</blue>> is the standard
  top-N pattern.

# TAG REFERENCE

  <<amber>>amber<</amber>> keywords. <<teal>>teal<</teal>> types. <<green>>green<</green>> strings.
  <<blue>>blue<</blue>> numerics. <<purple>>purple<</purple>> window/CTE syntax. <<red>>red<</red>>
  warnings. <<dim>>dim<</dim>> asides. <<bold>>bold<</bold>> emphasis.
