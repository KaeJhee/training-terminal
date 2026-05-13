# SQL · TIER 2 CONCEPTS (AMATEUR)

  <<dim>>Filtering gets richer. You stop saying "equal to" and start saying "in this<</dim>>
  <<dim>>range, in this set, matching this pattern."<</dim>>

  At this tier the queries answer questions a real shop manager actually asks:
  what's the average cost, who hasn't given us a phone number, find me anything
  in the 1990s.

# RANGES, SETS, PATTERNS

  <<amber>>BETWEEN<</amber>> is inclusive on both endpoints. It's syntactic sugar for two
  comparisons joined by <<amber>>AND<</amber>>.

      <<amber>>WHERE<</amber>> year <<amber>>BETWEEN<</amber>> <<blue>>1990<</blue>> <<amber>>AND<</amber>> <<blue>>1999<</blue>>

  <<amber>>IN<</amber>> tests membership in a small set. Cleaner than chained <<amber>>OR<</amber>>
  statements and easier to extend.

      <<amber>>WHERE<</amber>> status <<amber>>IN<</amber>> (<<green>>'Open'<</green>>, <<green>>'In Progress'<</green>>)

  <<amber>>LIKE<</amber>> does pattern matching. <<bold>>%<</bold>> matches any run of characters,
  <<bold>>_<</bold>> matches exactly one. <<amber>>NOT LIKE<</amber>> inverts.

      <<amber>>WHERE<</amber>> name <<amber>>LIKE<</amber>> <<green>>'K%'<</green>>          <<dim>>starts with K<</dim>>
      <<amber>>WHERE<</amber>> name <<amber>>LIKE<</amber>> <<green>>'%son'<</green>>        <<dim>>ends with son<</dim>>
      <<amber>>WHERE<</amber>> name <<amber>>LIKE<</amber>> <<green>>'_a%'<</green>>         <<dim>>a is the second letter<</dim>>

# NULL

  Missing data is its own thing. Three-valued logic: <<amber>>NULL<</amber>> is neither
  true nor false in any comparison. <<red>>= NULL<</red>> always returns nothing. Use
  <<amber>>IS NULL<</amber>> and <<amber>>IS NOT NULL<</amber>>.

  <<dim>>Why this matters: in customer records phone numbers, optional addresses,<</dim>>
  <<dim>>and unfilled-in fields are all NULLs. Filtering them needs the right operator<</dim>>
  <<dim>>or you get phantom empty results.<</dim>>

# AGGREGATES BEYOND COUNT

  <<amber>>SUM<</amber>>, <<amber>>AVG<</amber>>, <<amber>>MIN<</amber>>, <<amber>>MAX<</amber>> all reduce a column
  to a single value. They ignore NULLs. You can put several in one SELECT.

      <<amber>>SELECT<</amber>> <<amber>>MIN<</amber>>(total_cost), <<amber>>MAX<</amber>>(total_cost) <<amber>>FROM<</amber>> work_orders;

  <<amber>>ORDER BY<</amber>> x <<amber>>DESC<</amber>> <<amber>>LIMIT<</amber>> <<blue>>N<</blue>> is the top-N
  recipe. Order then trim. The reverse order doesn't make sense.

# CONDITIONAL EXPRESSIONS

  <<amber>>CASE<</amber>> <<amber>>WHEN<</amber>> cond <<amber>>THEN<</amber>> a <<amber>>ELSE<</amber>> b <<amber>>END<</amber>>
  is the SQL ternary. Use it inside <<amber>>SELECT<</amber>> to bucket continuous values
  or label rows.

  <<dim>>This is the building block for the pivot trick at Master tier. See<</dim>>
  <<dim>><</dim>><<qid:sql_mas_08>><<dim>>.<</dim>>

  NEXT TIER: joins. Once you can pull rows from one table cleanly, the next
  step is combining facts that live in two tables.

---

# EXAMPLE 1

  Find the most expensive open work_order. Two filters and a sort.

      <<amber>>SELECT<</amber>> id, total_cost
      <<amber>>FROM<</amber>> work_orders
      <<amber>>WHERE<</amber>> status = <<green>>'Open'<</green>>
      <<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>
      <<amber>>LIMIT<</amber>> <<blue>>1<</blue>>;

  <<dim>>LIMIT N is your top-N pattern. LIMIT 1 is the "single biggest" idiom.<</dim>>

# EXAMPLE 2

  Bucket continuous prices into named tiers. CASE creates a derived column.

      <<amber>>SELECT<</amber>> id,
             <<amber>>CASE<</amber>>
                 <<amber>>WHEN<</amber>> total_cost < <<blue>>500<</blue>>  <<amber>>THEN<</amber>> <<green>>'Small'<</green>>
                 <<amber>>WHEN<</amber>> total_cost < <<blue>>2000<</blue>> <<amber>>THEN<</amber>> <<green>>'Mid'<</green>>
                 <<amber>>ELSE<</amber>> <<green>>'Large'<</green>>
             <<amber>>END<</amber>> <<amber>>AS<</amber>> bucket
      <<amber>>FROM<</amber>> work_orders;

  <<dim>>Same trick that ML uses to discretize a continuous feature into bins for<</dim>>
  <<dim>>a tree model. The label column is the threshold's output.<</dim>>

# EXAMPLE 3

  Count by category, previewing GROUP BY at the next tier. Right now you can
  hand-count one bucket at a time:

      <<amber>>SELECT<</amber>> <<amber>>COUNT<</amber>>(*) <<amber>>FROM<</amber>> work_orders <<amber>>WHERE<</amber>> status = <<green>>'Open'<</green>>;
      <<amber>>SELECT<</amber>> <<amber>>COUNT<</amber>>(*) <<amber>>FROM<</amber>> work_orders <<amber>>WHERE<</amber>> status = <<green>>'Completed'<</green>>;

  <<dim>>Three queries for three statuses is fine for now. At Intermediate tier<</dim>>
  <<dim>>one <</dim>><<amber>>GROUP BY<</amber>><<dim>> gives you all categories in a single result. See<</dim>>
  <<dim>><</dim>><<qid:sql_int_03>><<dim>>.<</dim>>

