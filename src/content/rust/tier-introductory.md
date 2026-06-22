# RUST · TIER 1 CONCEPTS (INTRODUCTORY)

  <<dim>>Read this once. The first ten questions cover binding values, simple
  types, printing, and reading from small collections.<</dim>>

  Rust is a compiled, statically-typed systems language built around memory
  safety without a garbage collector. At this tier the goal is to bind
  values to names, give them types, and read them back.

# BINDING VALUES

  <<amber>>let<</amber>> binds a name. Bindings are <<bold>>immutable by default<</bold>> — add
  <<amber>>mut<</amber>> when you intend to reassign. Every statement ends with <<amber>>;<</amber>>.

      <<amber>>let<</amber>> garage = <<green>>"Terminal Auto"<</green>>;   <<dim>>type inferred: &str<</dim>>
      <<amber>>let<</amber>> <<amber>>mut<</amber>> bays = <<blue>>4<</blue>>;              <<dim>>mutable i32<</dim>>
      bays = <<blue>>5<</blue>>;                       <<dim>>ok, because mut<</dim>>

  <<red>>Booleans are lowercase<</red>> true/false — capital True/False is a Python
  habit that won't compile. Annotate a type with <<amber>>:<</amber>> when you want one
  explicitly.

# NUMBERS

  Integer literals default to <<teal>>i32<</teal>>; decimals to <<teal>>f64<</teal>>. An <<teal>>f64<</teal>>
  literal needs the decimal point (<<blue>>95.0<</blue>>, not <<blue>>95<</blue>>). A literal may
  carry a suffix to pin its type: <<blue>>0u8<</blue>>, <<blue>>1.0f64<</blue>>.

# PRINTING

  <<purple>>println!<</purple>> is a <<bold>>macro<</bold>> — the <<amber>>!<</amber>> marks it. <<amber>>{}<</amber>> is a
  placeholder filled by the arguments that follow.

      <<purple>>println!<</purple>>(<<green>>"bays open: {}"<</green>>, bays);

# COLLECTIONS AND TUPLES

  <<teal>>Vec<T><</teal>> is a growable array, built with the <<purple>>vec!<</purple>> macro and
  indexed with <<amber>>[i]<</amber>>. A <<bold>>tuple<</bold>> groups a fixed set of values, reached
  by position with <<amber>>.0<</amber>>, <<amber>>.1<</amber>>.

      <<amber>>let<</amber>> hours = <<purple>>vec!<</purple>>[<<blue>>9<</blue>>, <<blue>>10<</blue>>, <<blue>>11<</blue>>];
      <<amber>>let<</amber>> first = hours[<<blue>>0<</blue>>];        <<dim>>9<</dim>>
      <<amber>>let<</amber>> shift = (<<blue>>9<</blue>>, <<blue>>17<</blue>>);         <<dim>>(i32, i32)<</dim>>

# CONTROL FLOW AND FUNCTIONS

  <<amber>>if<</amber>> takes no parentheses and is an <<bold>>expression<</bold>> — it produces a
  value. <<amber>>match<</amber>> compares against patterns and must be exhaustive. <<amber>>fn<</amber>>
  declares a function; its final expression (no <<amber>>;<</amber>>) is what it returns.

      <<amber>>fn<</amber>> <<teal>>busy<</teal>>(n: <<teal>>i32<</teal>>) -> <<teal>>bool<</teal>> { n > <<blue>>8<</blue>> }

  NEXT TIER: owned <<teal>>String<</teal>> vs borrowed <<teal>>&str<</teal>>, <<teal>>Vec<</teal>> methods, and
  <<teal>>Option<</teal>> / <<teal>>Result<</teal>> for values that might be missing or fail. The
  shift is from "store and print" to "handle presence and absence."

---

# EXAMPLE 1

  Bind a few names of different types and let Rust infer where it can.

      <<amber>>let<</amber>> shop = <<green>>"Terminal Auto"<</green>>;
      <<amber>>let<</amber>> bays = <<blue>>4<</blue>>;                 <<dim>>i32<</dim>>
      <<amber>>let<</amber>> hourly: <<teal>>f64<</teal>> = <<blue>>95.0<</blue>>;      <<dim>>explicit f64<</dim>>
      <<amber>>let<</amber>> open = <<amber>>true<</amber>>;             <<dim>>bool, lowercase<</dim>>

  <<dim>>One binding per line. Inference handles the first two; the f64 is
  annotated because 95.0 alone would just be "some float."<</dim>>

# EXAMPLE 2

  Build a small Vec and a tuple, then read from each.

      <<amber>>let<</amber>> hours = <<purple>>vec!<</purple>>[<<blue>>9<</blue>>, <<blue>>10<</blue>>, <<blue>>11<</blue>>];
      <<amber>>let<</amber>> opening = hours[<<blue>>0<</blue>>];       <<dim>>9<</dim>>
      <<amber>>let<</amber>> shift = (<<blue>>9<</blue>>, <<blue>>17<</blue>>);
      <<amber>>let<</amber>> ends = shift.<<blue>>1<</blue>>;          <<dim>>17 — tuple field by position<</dim>>

  <<dim>>Vec indexing and tuple-field access both start at 0, but a tuple's
  fields use .0 / .1, not [0].<</dim>>

# EXAMPLE 3

  <<amber>>if<</amber>> is an expression, so it can feed a binding directly. A function
  returns its final expression.

      <<amber>>fn<</amber>> <<teal>>busy<</teal>>(n: <<teal>>i32<</teal>>) -> <<teal>>bool<</teal>> {
          n > <<blue>>8<</blue>>                      <<dim>>no semicolon: this is the return<</dim>>
      }
      <<amber>>let<</amber>> level = <<amber>>if<</amber>> busy(<<blue>>10<</blue>>) { <<green>>"high"<</green>> } <<amber>>else<</amber>> { <<green>>"low"<</green>> };

  <<dim>>A trailing semicolon on that last function line would discard the
  value and return the unit type instead. Leave it off to return.<</dim>>

# EXAMPLE 4

  A preview of Amateur tier: <<teal>>Option<i32><</teal>> represents a value that
  might be missing, and <<amber>>match<</amber>> handles both cases.

      <<amber>>let<</amber>> maybe_bay: <<teal>>Option<i32><</teal>> = <<amber>>Some<</amber>>(<<blue>>3<</blue>>);
      <<amber>>let<</amber>> note = <<amber>>match<</amber>> maybe_bay {
          <<amber>>Some<</amber>>(n) => n,
          <<amber>>None<</amber>> => <<blue>>0<</blue>>,
      };

  <<dim>>Next tier leans on this: Option, Result, and match together are how
  Rust handles "might not be there" without null.<</dim>>
