# RUST · TIER 2 CONCEPTS (AMATEUR)

  <<dim>>This tier is about collections that grow, strings you own, and values
  that might be missing or might fail.<</dim>>

  Introductory bound and printed values. Now you build them up: push onto a
  <<teal>>Vec<</teal>>, own a <<teal>>String<</teal>>, and model "maybe absent" with <<teal>>Option<</teal>> and
  "maybe failed" with <<teal>>Result<</teal>> — Rust's stand-ins for null and exceptions.

# VECTORS AND STRINGS

  <<teal>>Vec<T><</teal>> starts empty with <<teal>>Vec<</teal>>::new() and grows with <<purple>>.push<</purple>>;
  pushing needs <<amber>>mut<</amber>>. An owned <<teal>>String<</teal>> (heap, growable) is distinct
  from a borrowed <<teal>>&str<</teal>> slice; build one with <<teal>>String<</teal>>::from.

      <<amber>>let<</amber>> <<amber>>mut<</amber>> queue: <<teal>>Vec<i32><</teal>> = <<teal>>Vec<</teal>>::new();
      queue.<<purple>>push<</purple>>(<<blue>>7<</blue>>);
      <<amber>>let<</amber>> shop: <<teal>>String<</teal>> = <<teal>>String<</teal>>::from(<<green>>"Terminal"<</green>>);

  <<purple>>.len()<</purple>> returns the element count as <<teal>>usize<</teal>> — a method, <<red>>not a
  field, and not .length()<</red>>.

# OPTION: MAYBE A VALUE

  <<teal>>Option<T><</teal>> is either <<amber>>Some(v)<</amber>> or <<amber>>None<</amber>>. It's how Rust says "this
  might be empty" without a null that could crash you later.

      <<amber>>let<</amber>> found: <<teal>>Option<i32><</teal>> = <<amber>>Some<</amber>>(<<blue>>10<</blue>>);

  Pull the value out safely with <<purple>>.unwrap_or<</purple>>(default), or branch with
  <<amber>>if let<</amber>> (one case) or <<amber>>match<</amber>> (both cases). Reach for <<amber>>if let<</amber>> when
  you only care about the <<amber>>Some<</amber>> case and want to ignore <<amber>>None<</amber>>; reach
  for <<amber>>match<</amber>> when both arms do real work and the compiler should force
  you to handle each.

      <<amber>>if let<</amber>> <<amber>>Some<</amber>>(v) = found { <<purple>>println!<</purple>>(<<green>>"{}"<</green>>, v); }

# RESULT: MAYBE A FAILURE

  <<teal>>Result<T, E><</teal>> is <<amber>>Ok(v)<</amber>> for success or <<amber>>Err(e)<</amber>> for failure.
  A function that can fail returns one; the caller decides what to do.

      <<amber>>fn<</amber>> <<teal>>half<</teal>>(n: <<teal>>i32<</teal>>) -> <<teal>>Result<i32, String><</teal>> {
          <<amber>>if<</amber>> n % <<blue>>2<</blue>> == <<blue>>0<</blue>> { <<amber>>Ok<</amber>>(n / <<blue>>2<</blue>>) } <<amber>>else<</amber>> { <<amber>>Err<</amber>>(<<teal>>String<</teal>>::from(<<green>>"odd"<</green>>)) }
      }

  NEXT TIER: <<bold>>ownership<</bold>> and <<bold>>borrowing<</bold>> — passing a value by reference
  (<<amber>>&<</amber>>) instead of moving it — plus iterators and closures for transforming
  collections without writing the loop yourself.

---

# EXAMPLE 1

  Grow a vector, then ask it for its length.

      <<amber>>let<</amber>> <<amber>>mut<</amber>> tickets: <<teal>>Vec<i32><</teal>> = <<teal>>Vec<</teal>>::new();
      tickets.<<purple>>push<</purple>>(<<blue>>101<</blue>>);
      tickets.<<purple>>push<</purple>>(<<blue>>102<</blue>>);
      <<amber>>let<</amber>> open = tickets.<<purple>>len<</purple>>();    <<dim>>2, a usize<</dim>>

  <<dim>>Without <<amber>>mut<</amber>> the push lines would not compile. .len() reads the
  count back; it never changes the vector.<</dim>>

# EXAMPLE 2

  Own a String, then borrow it as a &str to read without taking ownership.

      <<amber>>let<</amber>> make = <<teal>>String<</teal>>::from(<<green>>"Nissan"<</green>>);
      <<amber>>let<</amber>> view: &<<teal>>str<</teal>> = &make;      <<dim>>a borrowed slice of make<</dim>>
      <<purple>>println!<</purple>>(<<green>>"{}"<</green>>, view);

  <<dim>>make owns the text; view borrows it. Both can be read here because a
  shared borrow doesn't move the owner. More on borrowing next tier.<</dim>>

# EXAMPLE 3

  Handle an Option both ways: a default with unwrap_or, and a branch with
  match.

      <<amber>>let<</amber>> reading: <<teal>>Option<f64><</teal>> = <<amber>>None<</amber>>;
      <<amber>>let<</amber>> safe = reading.<<purple>>unwrap_or<</purple>>(<<blue>>0.0<</blue>>);   <<dim>>0.0, since None<</dim>>
      <<amber>>let<</amber>> tag = <<amber>>match<</amber>> reading {
          <<amber>>Some<</amber>>(v) => v,
          <<amber>>None<</amber>> => <<blue>>-1.0<</blue>>,
      };

  <<dim>>unwrap_or gives a fallback in one move; match lets each arm do
  different work. Reach for match when the cases diverge.<</dim>>

# EXAMPLE 4

  A preview of Intermediate tier: borrow a Vec by reference so a function
  can read it without taking ownership.

      <<amber>>fn<</amber>> <<teal>>total<</teal>>(xs: &<<teal>>Vec<i32><</teal>>) -> <<teal>>i32<</teal>> {
          <<amber>>let<</amber>> <<amber>>mut<</amber>> sum = <<blue>>0<</blue>>;
          <<amber>>for<</amber>> v <<amber>>in<</amber>> xs { sum += v; }
          sum
      }

  <<dim>>The <<amber>>&<</amber>> means total borrows the vector; the caller keeps owning it.
  Next tier replaces this hand-written loop with .iter().sum().<</dim>>
