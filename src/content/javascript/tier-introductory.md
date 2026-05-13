# JAVASCRIPT · TIER 1 CONCEPTS (INTRODUCTORY)

  <<dim>>Read this once. The first ten questions cover binding values, simple
  collections, and getting them back out.<</dim>>

  JavaScript is a dynamically-typed language that runs in browsers, on
  servers (Node.js), and almost everywhere else. At this tier the goal is
  to bind values to names, build small collections, and read from them.

# BINDING NAMES

  Three keywords for declaring variables. <<amber>>const<</amber>> is the default —
  use it whenever the binding won't be reassigned. <<amber>>let<</amber>> when you
  need reassignment. <<amber>>var<</amber>> is legacy; you'll see it in older code
  but new code uses const/let.

      <<amber>>const<</amber>> garage_name = <<green>>'Terminal Auto'<</green>>
      <<amber>>let<</amber>> open_jobs = <<blue>>7<</blue>>
      <<amber>>const<</amber>> is_open = <<amber>>true<</amber>>

  Single or double quotes both make strings. Pick one and stay consistent.
  <<red>>Booleans are lowercase<</red>> true/false — capitalized True/False is a
  Python habit that throws a ReferenceError in JS.

# COLLECTIONS

  Arrays are ordered, mutable lists. Objects are key-value maps. These
  cover most data shapes at this tier.

      <<amber>>const<</amber>> mechanics = [<<green>>'Kris'<</green>>, <<green>>'Alex'<</green>>, <<green>>'Sam'<</green>>]
      <<amber>>const<</amber>> customer = { id: <<blue>>1<</blue>>, name: <<green>>'Alice'<</green>> }

  <<bold>>arr[i]<</bold>> indexes into an array (zero-based). <<bold>>arr.length<</bold>>
  gives the count — <<red>>property, not function, no parentheses<</red>>.
  <<bold>>obj.key<</bold>> reads dot-notation; <<bold>>obj["key"]<</bold>> is the bracket
  form for keys with spaces or computed names.

      mechanics[<<blue>>0<</blue>>]      <<dim>>'Kris'<</dim>>
      mechanics.length    <<dim>>3<</dim>>
      customer.name       <<dim>>'Alice'<</dim>>

# OUTPUT

  <<amber>>console.log<</amber>>(x) writes x to stdout followed by a newline. With
  multiple arguments it joins them with a space. This is JavaScript's
  print().

      console.log(<<green>>'Shop open'<</green>>)

# TEMPLATE LITERALS

  Backticks (not quotes) let you interpolate expressions inside a string
  with <<bold>>${...}<</bold>>. Cleaner than concatenation with <<bold>>+<</bold>>.

      <<amber>>const<</amber>> greeting = <<green>>`Welcome to ${shop_name}`<</green>>

  <<dim>>The backtick is the single subtle syntax point at this tier. The
  string is otherwise identical to a normal one.<</dim>>

  NEXT TIER: array methods (map/filter/reduce), destructuring, default
  arguments, and the start of light ML framing — one-hot encoding, threshold
  filtering. The shift is from "store data" to "transform data."

---

# EXAMPLE 1

  Bind a few names of different types and read them back. JavaScript
  figures out the types from the values.

      <<amber>>const<</amber>> shop = <<green>>'Terminal Auto'<</green>>
      <<amber>>const<</amber>> open_jobs = <<blue>>7<</blue>>
      <<amber>>const<</amber>> avg_ticket = <<blue>>412.50<</blue>>
      <<amber>>const<</amber>> is_open = <<amber>>true<</amber>>
      console.log(shop, open_jobs, avg_ticket, is_open)

  <<dim>>One assignment per line is the convention. console.log with multiple
  arguments space-separates them — that's just what console.log does, not
  a feature of the variables.<</dim>>

# EXAMPLE 2

  Build a small object literal and read a property. Dot notation is
  cleanest for known keys.

      <<amber>>const<</amber>> car = { make: <<green>>'Nissan'<</green>>, model: <<green>>'Skyline GT-R'<</green>>, year: <<blue>>1996<</blue>> }
      console.log(car.make)            <<dim>>'Nissan'<</dim>>
      console.log(car[<<green>>'model'<</green>>])         <<dim>>'Skyline GT-R' (bracket form)<</dim>>

  <<dim>>Reading a property that doesn't exist returns <</dim>><<amber>>undefined<</amber>><<dim>>,
  not an error — different from Python, which raises KeyError. Defensive code
  uses optional chaining (<</dim>><<bold>>car?.make?.brand<</bold>><<dim>>) at higher tiers.<</dim>>

# EXAMPLE 3

  Branch on a value, previewing arrays and loops at the next tier. You can
  already check one item at a time:

      <<amber>>const<</amber>> cost = <<blue>>1500<</blue>>
      <<amber>>if<</amber>> (cost > <<blue>>1000<</blue>>) {
          console.log(<<green>>'High'<</green>>)
      } <<amber>>else<</amber>> {
          console.log(<<green>>'Low'<</green>>)
      }

  <<dim>>At Amateur tier you'll meet <</dim>><<amber>>map<</amber>><<dim>> and <</dim>><<amber>>filter<</amber>><<dim>>,
  which run the same conditional logic across every element in an array
  without writing the loop yourself. The branching shape stays identical;
  the array method just feeds the variable repeatedly. See <</dim>><<qid:js_am_02>><<dim>>.<</dim>>
