# SQL · TIER 3 CONCEPTS (INTERMEDIATE)

  <<dim>>Two new ideas that let you ask vastly harder questions: combining tables and<</dim>>
  <<dim>>collapsing groups. Most production queries use both.<</dim>>

# JOINS

  Real schemas split related facts across tables. Customers in one, vehicles in
  another, work_orders in a third. A join walks them side by side, matching
  rows on a shared key.

      <<amber>>SELECT<</amber>> customers.name, vehicles.make
      <<amber>>FROM<</amber>> customers
      <<amber>>JOIN<</amber>> vehicles <<amber>>ON<</amber>> customers.id = vehicles.customer_id;

  Bare <<amber>>JOIN<</amber>> is an inner join. Only rows that match on both sides survive.
  <<amber>>LEFT JOIN<</amber>> keeps every row from the left table, filling NULL where the
  right has no match. That distinction matters when you want a customer's
  vehicle count <<bold>>including zeros<</bold>>.

  <<dim>>A vehicle row without a matching customer is a referential bug. A customer<</dim>>
  <<dim>>row without a matching vehicle is a normal business state.<</dim>>

# AGGREGATING IN GROUPS

  <<amber>>GROUP BY<</amber>> divides the rows into buckets and runs an aggregate per
  bucket. The output has one row per group. Every column in the <<amber>>SELECT<</amber>>
  must either be in the <<amber>>GROUP BY<</amber>> or be wrapped in an aggregate.

      <<amber>>SELECT<</amber>> status, <<amber>>COUNT<</amber>>(*) <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> status;

  This is the right tool when you want a count per category, a sum per
  customer, or an average per mechanic.

# WHERE VS HAVING

  Two filters, two stages. <<amber>>WHERE<</amber>> runs before grouping, on individual
  rows. <<amber>>HAVING<</amber>> runs after grouping, on the aggregated result.

      <<amber>>WHERE<</amber>>  status = <<green>>'Completed'<</green>>   <<dim>>drops uncompleted rows<</dim>>
      <<amber>>HAVING<</amber>> <<amber>>COUNT<</amber>>(*) >= <<blue>>2<</blue>>            <<dim>>drops small groups<</dim>>

  Putting an aggregate inside <<amber>>WHERE<</amber>> is an error. Putting a row predicate
  inside <<amber>>HAVING<</amber>> is legal but slow.

# JOINING THREE TABLES

  Chain <<amber>>JOIN<</amber>> clauses. Each one matches the running result against the
  next table. Order doesn't change the answer for inner joins, only LEFT joins.

      <<amber>>FROM<</amber>> work_orders
      <<amber>>JOIN<</amber>> vehicles  <<amber>>ON<</amber>> work_orders.vehicle_id = vehicles.id
      <<amber>>JOIN<</amber>> customers <<amber>>ON<</amber>> vehicles.customer_id = customers.id

  <<dim>>This is the canonical "trace a transaction back to its root entity"<</dim>>
  <<dim>>pattern. See <</dim>><<qid:sql_int_09>><<dim>>.<</dim>>

# ROUNDING AND ALIASING

  <<amber>>ROUND<</amber>>(x, n) trims float noise from averages. <<amber>>AS<</amber>> gives an
  expression a friendly column name. Both small but they make output readable.

  NEXT TIER: window functions. Same idea as GROUP BY but the original rows
  survive. You'll be able to rank, partition, and run cumulative sums.

---

# EXAMPLE 1

  Average cost per status. One row per group, one aggregate per row.

      <<amber>>SELECT<</amber>> status, <<amber>>ROUND<</amber>>(<<amber>>AVG<</amber>>(total_cost), <<blue>>2<</blue>>) <<amber>>AS<</amber>> avg_cost
      <<amber>>FROM<</amber>> work_orders
      <<amber>>GROUP BY<</amber>> status;

  <<dim>>ROUND keeps the output readable. AS gives the aggregate a name so you<</dim>>
  <<dim>>can ORDER BY it, reference it elsewhere, or read the result without squinting<</dim>>
  <<dim>>at "AVG(total_cost)".<</dim>>

# EXAMPLE 2

  LEFT JOIN to count children, including zeros. The grouping happens on the
  parent's id so each customer appears once even with no children.

      <<amber>>SELECT<</amber>> customers.name, <<amber>>COUNT<</amber>>(vehicles.id) <<amber>>AS<</amber>> vehicle_count
      <<amber>>FROM<</amber>> customers
      <<amber>>LEFT JOIN<</amber>> vehicles <<amber>>ON<</amber>> customers.id = vehicles.customer_id
      <<amber>>GROUP BY<</amber>> customers.id;

  <<dim>>COUNT(vehicles.id) instead of COUNT(*) so a customer with no vehicles<</dim>>
  <<dim>>counts as zero, not one. COUNT skips NULLs.<</dim>>

# EXAMPLE 3

  Two filtering stages, previewing window functions. You want top spenders
  whose group is large enough to be meaningful.

      <<amber>>SELECT<</amber>> customers.id, customers.name, <<amber>>SUM<</amber>>(work_orders.total_cost) <<amber>>AS<</amber>> spend
      <<amber>>FROM<</amber>> customers
      <<amber>>JOIN<</amber>> vehicles    <<amber>>ON<</amber>> vehicles.customer_id = customers.id
      <<amber>>JOIN<</amber>> work_orders <<amber>>ON<</amber>> work_orders.vehicle_id = vehicles.id
      <<amber>>GROUP BY<</amber>> customers.id
      <<amber>>HAVING<</amber>> <<amber>>COUNT<</amber>>(work_orders.id) >= <<blue>>2<</blue>>
      <<amber>>ORDER BY<</amber>> spend <<amber>>DESC<</amber>>;

  <<dim>>At the next tier you'll add <</dim>><<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (...) <<dim>>to<</dim>>
  <<dim>>number these without losing the per-row detail. GROUP BY destroys row-level<</dim>>
  <<dim>>rows; window functions preserve them.<</dim>>

