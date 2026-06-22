# RUST · TIER 3 CONCEPTS (INTERMEDIATE)

  <<dim>>The heart of Rust: who owns a value, who may borrow it, and how to
  transform collections with iterators and closures.<</dim>>

  Every value has a single owner. You can hand out <<bold>>borrows<</bold>> — temporary
  read or write access — but the compiler enforces one rule that prevents
  whole classes of bugs. Then iterators let you express "do this to each
  element" without a manual loop.

# OWNERSHIP AND BORROWING

  Passing a value by name <<bold>>moves<</bold>> it. To let a function read a value
  without taking it, pass a <<bold>>borrow<</bold>> with <<amber>>&<</amber>>. A shared borrow <<amber>>&T<</amber>>
  is read-only; an exclusive borrow <<amber>>&mut T<</amber>> can modify.

      <<amber>>fn<</amber>> <<teal>>peek<</teal>>(xs: &<<teal>>Vec<i32><</teal>>)      <<dim>>reads, caller keeps ownership<</dim>>
      <<amber>>fn<</amber>> <<teal>>grow<</teal>>(xs: &<<amber>>mut<</amber>> <<teal>>Vec<i32><</teal>>)  <<dim>>can push; needs mut access<</dim>>

  The one rule the borrow checker enforces, at compile time:

      at any moment, a value has EITHER
        - any number of  &T   shared borrows   (readers)   OR
        - exactly one    &mut T exclusive borrow (writer)
      never both at once

  <<red>>A writer and a reader cannot coexist.<</red>> That is what stops data races
  and use-after-free before the program ever runs.

# ITERATORS

  <<purple>>.iter()<</purple>> turns a collection into a lazy sequence of <<amber>>&T<</amber>> references.
  Chain adapters, then finish with a consumer.

      <<amber>>let<</amber>> total: <<teal>>i32<</teal>> = xs.<<purple>>iter<</purple>>().<<purple>>sum<</purple>>();
      <<amber>>let<</amber>> evens: <<teal>>Vec<i32><</teal>> = xs.<<purple>>iter<</purple>>().<<purple>>filter<</purple>>(|&x| x % <<blue>>2<</blue>> == <<blue>>0<</blue>>).<<purple>>copied<</purple>>().<<purple>>collect<</purple>>();

  <<purple>>.map<</purple>> transforms, <<purple>>.filter<</purple>> keeps, <<purple>>.fold<</purple>> accumulates,
  <<purple>>.sum<</purple>>/<<purple>>.count<</purple>>/<<purple>>.collect<</purple>> finish.

# CLOSURES

  A closure is an inline function written <<amber>>|args| body<</amber>>; it can capture
  variables from the surrounding scope. Since <<purple>>.iter()<</purple>> yields references,
  closures often deref their argument.

      xs.<<purple>>iter<</purple>>().<<purple>>map<</purple>>(|&x| x * x)    <<dim>>|&x| binds x as the value<</dim>>
      xs.<<purple>>iter<</purple>>().<<purple>>map<</purple>>(|x| *x * *x)   <<dim>>or deref in the body<</dim>>

  Add <<amber>>move<</amber>> to force the closure to <<bold>>own<</bold>> its captures — required when
  the closure outlives the current scope (e.g. handed to a thread).

  NEXT TIER: <<bold>>traits<</bold>> (shared behavior across types) and <<bold>>generics<</bold>>
  (<<amber>><T><</amber>> with bounds). You'll define an interface once and implement it
  for many types, and write functions that work over any type that fits.

---

# EXAMPLE 1

  Borrow a slice to read it; take &mut to change it. Two functions, two
  kinds of access.

      <<amber>>fn<</amber>> <<teal>>biggest<</teal>>(xs: &<<teal>>Vec<i32><</teal>>) -> <<teal>>i32<</teal>> {
          <<amber>>let<</amber>> <<amber>>mut<</amber>> best = xs[<<blue>>0<</blue>>];
          <<amber>>for<</amber>> &v <<amber>>in<</amber>> xs { <<amber>>if<</amber>> v > best { best = v; } }
          best
      }
      <<amber>>fn<</amber>> <<teal>>bump<</teal>>(xs: &<<amber>>mut<</amber>> <<teal>>Vec<i32><</teal>>) { xs.<<purple>>push<</purple>>(<<blue>>0<</blue>>); }

  <<dim>>biggest only reads, so &Vec is enough. bump mutates, so it needs
  &mut. You could not hold both borrows at the same time.<</dim>>

# EXAMPLE 2

  Replace a manual loop with an iterator chain: keep the big readings,
  scale them, collect the result.

      <<amber>>let<</amber>> readings = <<purple>>vec!<</purple>>[<<blue>>0.2<</blue>>, <<blue>>0.9<</blue>>, <<blue>>0.5<</blue>>];
      <<amber>>let<</amber>> strong: <<teal>>Vec<f64><</teal>> = readings.<<purple>>iter<</purple>>()
          .<<purple>>filter<</purple>>(|&r| r > <<blue>>0.4<</blue>>)
          .<<purple>>map<</purple>>(|r| r * <<blue>>10.0<</blue>>)
          .<<purple>>collect<</purple>>();

  <<dim>>Each adapter is lazy; nothing runs until .collect() consumes the chain.
  Read it top to bottom as a pipeline: filter, then map, then gather.<</dim>>

# EXAMPLE 3

  A closure can capture a value from its scope. Here it captures a
  threshold and counts how many readings clear it.

      <<amber>>let<</amber>> cutoff = <<blue>>0.5<</blue>>;
      <<amber>>let<</amber>> passing = readings.<<purple>>iter<</purple>>().<<purple>>filter<</purple>>(|&r| r >= cutoff).<<purple>>count<</purple>>();

  <<dim>>cutoff is captured by the closure automatically. Because f64 is Copy,
  no move is needed; for a captured Vec or String you would add move.<</dim>>

# EXAMPLE 4

  A preview of Experienced tier: a <<bold>>generic<</bold>> function that works for any
  type implementing a <<teal>>trait<</teal>>. This one debug-prints any such value.

      <<amber>>fn<</amber>> <<teal>>describe<</teal>><<amber>><T: std::fmt::Debug><</amber>>(item: &<<teal>>T<</teal>>) {
          <<purple>>println!<</purple>>(<<green>>"{:?}"<</green>>, item);
      }

  <<dim>>The <<amber>><T: Debug><</amber>> bound says "any type T that can be debug-printed."
  Next tier defines traits and implements them, instead of just requiring
  one as a bound here.<</dim>>
