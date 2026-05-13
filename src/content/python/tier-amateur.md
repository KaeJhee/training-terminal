# PYTHON · TIER 2 CONCEPTS (AMATEUR)

  <<dim>>Loops, functions, and the iterables story. Once these click, you can write
  any procedural script.<</dim>>

# FOR LOOPS

  <<amber>>for<</amber>> iterates over an iterable. Lists, strings, dicts, ranges, files,
  anything that implements iteration.

      <<amber>>for<</amber>> m <<amber>>in<</amber>> mechanics:
          <<amber>>print<</amber>>(m)

  The variable <<bold>>m<</bold>> takes each value in turn. The loop body runs once per
  item. No counter to manage by hand. If you need an index, use
  <<amber>>enumerate<</amber>>() at Experienced tier.

# WHILE LOOPS

  <<amber>>while<</amber>> runs as long as the condition is truthy. You manage the
  termination yourself. Common pattern: maintain a counter and stop at a
  threshold.

      nums, i = [], <<blue>>1<</blue>>
      <<amber>>while<</amber>> i <= <<blue>>5<</blue>>:
          nums.append(i)
          i += <<blue>>1<</blue>>

  <<red>>Forgetting to update the counter is the easiest way to hang Python.<</red>>
  Use <<amber>>for<</amber>> when the iteration count is known up front.

# FUNCTIONS

  <<amber>>def<</amber>> declares a reusable block. The signature names the parameters.
  <<amber>>return<</amber>> sends a value back; without it the function returns None.

      <<amber>>def<</amber>> <<teal>>add_two<</teal>>(x, y):
          <<amber>>return<</amber>> x + y

  Functions don't have type annotations at this tier (we'll get there at
  Master). Parameters are positional by default but can be passed by name.

# TUPLES AND UNPACKING

  Tuples are immutable, ordered sequences. Parentheses are optional. The
  killer feature is multi-assignment: a tuple on the right binds to a tuple
  of names on the left.

      make, year = <<green>>'Nissan'<</green>>, <<blue>>1996<</blue>>
      a, b = b, a            <<dim>>swap without a temp<</dim>>

  Functions can return tuples to give back multiple values, and the caller
  unpacks the result.

# WORKHORSE BUILT-INS

  <<amber>>sum<</amber>>(iterable) totals numbers. <<amber>>sorted<</amber>>(iterable) returns a
  new sorted list. <<amber>>sorted<</amber>>([..], reverse=<<amber>>True<</amber>>) sorts high to
  low. <<amber>>zip<</amber>>(a, b) pairs two iterables element-wise.

      <<amber>>list<</amber>>(<<amber>>zip<</amber>>([<<blue>>1<</blue>>, <<blue>>2<</blue>>], [<<green>>'a'<</green>>, <<green>>'b'<</green>>]))   <<dim>>[(1, 'a'), (2, 'b')]<</dim>>

  Strings have <<bold>>.split<</bold>>(sep) and <<bold>>.count<</bold>>(sub). Lists have
  <<bold>>.append<</bold>>, <<bold>>.count<</bold>>, <<bold>>.sort<</bold>> (in place).

# F-STRING BASICS

  <<green>>f'...'<</green>> interpolates expressions. Curly braces hold the value.

      <<green>>f'Hello, {name}'<</green>>

  At Intermediate tier you'll learn formatting specifiers like
  <<bold>>:.2f<</bold>> and <<bold>>:,<</bold>>.

  NEXT TIER: list and dict comprehensions, lambdas, <<amber>>map<</amber>> and
  <<amber>>filter<</amber>>, default arguments. The shift is from "loop and append" to
  "describe the result."

---

# EXAMPLE 1

  Iterate a list and accumulate. Vanilla for-loop pattern.

      total_cost = <<blue>>0<</blue>>
      <<amber>>for<</amber>> order <<amber>>in<</amber>> [<<blue>>100<</blue>>, <<blue>>250<</blue>>, <<blue>>75<</blue>>, <<blue>>300<</blue>>]:
          total_cost += order
      <<amber>>print<</amber>>(total_cost)

  <<dim>>This is what <</dim>><<amber>>sum<</amber>>()<<dim>> does internally. The built-in is
  shorter and faster. Reach for it whenever you see "loop, accumulate, return
  the total."<</dim>>

# EXAMPLE 2

  Define a function with a default argument. Defaults are evaluated once at
  definition time.

      <<amber>>def<</amber>> <<teal>>markup<</teal>>(base, rate=<<blue>>0.20<</blue>>):
          <<amber>>return<</amber>> base * (<<blue>>1<</blue>> + rate)

      <<amber>>print<</amber>>(<<teal>>markup<</teal>>(<<blue>>100<</blue>>))         <<dim>>120.0 (rate defaulted)<</dim>>
      <<amber>>print<</amber>>(<<teal>>markup<</teal>>(<<blue>>100<</blue>>, <<blue>>0.40<</blue>>))   <<dim>>140.0 (rate explicit)<</dim>>

  <<dim>>A subtle gotcha: never use mutable default values like an empty list or
  empty dict. They share state across calls. Use None and assign inside the body.<</dim>>

# EXAMPLE 3

  Build a list with a loop, previewing list comprehensions. Right now:

      doubled = []
      <<amber>>for<</amber>> x <<amber>>in<</amber>> [<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>, <<blue>>4<</blue>>]:
          doubled.append(x * <<blue>>2<</blue>>)

  <<dim>>At the next tier the same logic compresses to one line:

  <</dim>>      doubled = [x * <<blue>>2<</blue>> <<amber>>for<</amber>> x <<amber>>in<</amber>> [<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>, <<blue>>4<</blue>>]]

  <<dim>>Same loop, same result, but the shape of the code matches the shape of
  the data: one input per output. See <</dim>><<qid:py_int_06>><<dim>>.<</dim>>
