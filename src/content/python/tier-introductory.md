# PYTHON · TIER 1 CONCEPTS (INTRODUCTORY)

  <<dim>>The first ten questions cover variables, simple collections, basic control
  flow, and the built-in conversions you'll use forever.<</dim>>

  Python is a high-level interpreted language. You don't declare variable
  types or compile anything. You write expressions and Python evaluates them.
  At this tier the goal is to bind values to names and pull them back out.

# BINDING NAMES

  <<amber>>=<</amber>> is assignment, not equality. The right side is evaluated, then
  the result is bound to the name on the left.

      garage_name = <<green>>'Terminal Auto'<</green>>
      count = <<blue>>42<</blue>>
      is_open = <<amber>>True<</amber>>

  Single or double quotes both make strings. Pick one and stay consistent.
  <<amber>>True<</amber>> / <<amber>>False<</amber>> are capitalized. <<amber>>None<</amber>> means "no value."

# COLLECTIONS

  Two basic containers at this tier. Lists are ordered and mutable.
  Dictionaries map keys to values.

      mechanics = [<<green>>'Kris'<</green>>, <<green>>'Alex'<</green>>, <<green>>'Sam'<</green>>]
      customer  = {<<green>>'id'<</green>>: <<blue>>1<</blue>>, <<green>>'name'<</green>>: <<green>>'Alice'<</green>>}

  <<amber>>len<</amber>>(obj) returns the size. Brackets index into a list (zero-based)
  or look up a dict key.

      mechanics[<<blue>>0<</blue>>]      <<dim>>'Kris'<</dim>>
      customer[<<green>>'name'<</green>>] <<dim>>'Alice'<</dim>>

# CONVERSIONS

  Python won't auto-cast strings and numbers. You convert explicitly.

      year = <<amber>>int<</amber>>(<<green>>'2024'<</green>>)         <<dim>>'2024' -> 2024<</dim>>
      price = <<amber>>float<</amber>>(<<green>>'15.50'<</green>>)     <<dim>>'15.50' -> 15.5<</dim>>
      label = <<amber>>str<</amber>>(<<blue>>42<</blue>>)             <<dim>>42 -> '42'<</dim>>

  <<red>>int('hello') raises ValueError<</red>>. Conversions can fail. At Experienced
  tier you'll wrap them in try/except.

# CONDITIONALS

  <<amber>>if<</amber>> runs a block when the condition is truthy. The colon and
  indentation aren't optional, they're the syntax.

      <<amber>>if<</amber>> cost > <<blue>>1000<</blue>>:
          <<amber>>print<</amber>>(<<green>>'High'<</green>>)

  Indent the block four spaces. Tabs technically work but mixing them with
  spaces is the most common syntax-error cause for beginners.

# OUTPUT

  <<amber>>print<</amber>>(x) writes x to stdout followed by a newline. With multiple
  arguments it joins them with a space.

  NEXT TIER: loops, functions, and the workhorse built-ins like <<amber>>sum<</amber>>,
  <<amber>>sorted<</amber>>, <<amber>>zip<</amber>>. You'll also meet tuples, while loops, and
  string methods like <<bold>>.split<</bold>>() and <<bold>>.count<</bold>>().

---

# EXAMPLE 1

  Bind a few names and read them back. Python figures out the types.

      shop = <<green>>'Terminal Auto'<</green>>
      open_jobs = <<blue>>7<</blue>>
      avg_ticket = <<blue>>412.50<</blue>>
      <<amber>>print<</amber>>(shop, open_jobs, avg_ticket)

  <<dim>>One assignment per line. The output prints the three values
  space-separated because that's what print does with multiple args.<</dim>>

# EXAMPLE 2

  Build a small dict and read a value out. Square brackets do lookup.

      car = {<<green>>'make'<</green>>: <<green>>'Nissan'<</green>>, <<green>>'model'<</green>>: <<green>>'Skyline GT-R'<</green>>, <<green>>'year'<</green>>: <<blue>>1996<</blue>>}
      <<amber>>print<</amber>>(car[<<green>>'make'<</green>>])

  <<dim>>Looking up a missing key raises KeyError. At Intermediate tier you'll
  meet <</dim>><<bold>>.get<</bold>>(<<green>>'k'<</green>>, default)<<dim>> for safe access. See
  <</dim>><<qid:py_int_08>><<dim>>.<</dim>>

# EXAMPLE 3

  Branch on a value, previewing loops at the next tier. You can already check
  one item at a time:

      cost = <<blue>>1500<</blue>>
      <<amber>>if<</amber>> cost > <<blue>>1000<</blue>>:
          <<amber>>print<</amber>>(<<green>>'High'<</green>>)
      <<amber>>else<</amber>>:
          <<amber>>print<</amber>>(<<green>>'Low'<</green>>)

  <<dim>>At Amateur tier a <</dim>><<amber>>for<</amber>><<dim>> loop runs the same check across
  every item in a list automatically. The branching shape stays identical;
  the loop just feeds the variable repeatedly. See <</dim>><<qid:py_am_01>><<dim>>.<</dim>>
