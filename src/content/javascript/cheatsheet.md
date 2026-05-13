# JAVASCRIPT CHEATSHEET

  <<dim>>A working reference for the whole language. Skim it once, come back when stuck.<</dim>>

# VARIABLES AND TYPES

  Three declaration keywords. <<amber>>const<</amber>> for values that won't be
  reassigned, <<amber>>let<</amber>> for ones that will, <<amber>>var<</amber>> for legacy code
  you're maintaining.

      <<amber>>const<</amber>> garage = <<green>>'Terminal Auto'<</green>>
      <<amber>>let<</amber>> count = <<blue>>42<</blue>>
      <<amber>>const<</amber>> active = <<amber>>true<</amber>>

  <<red>>Booleans are lowercase<</red>>: <<amber>>true<</amber>> / <<amber>>false<</amber>>, not True/False.
  <<amber>>null<</amber>> is "no value"; <<amber>>undefined<</amber>> is "not yet set." They're
  different types and the distinction matters.

# COLLECTIONS

  Arrays are ordered, mutable, zero-indexed. Objects are key-value maps.

      <<amber>>const<</amber>> cars = [<<green>>'Skyline'<</green>>, <<green>>'Supra'<</green>>]
      <<amber>>const<</amber>> car = { make: <<green>>'Nissan'<</green>>, year: <<blue>>1996<</blue>> }

  <<bold>>arr[i]<</bold>> indexes. <<bold>>arr.length<</bold>> is the count — a property,
  <<red>>no parentheses<</red>>. <<bold>>obj.key<</bold>> reads dot notation. <<bold>>obj[k]<</bold>>
  reads via a computed key. <<dim>>See <<qid:js_intro_07>>.<</dim>>

# CONTROL FLOW

  <<amber>>if<</amber>> / <<amber>>else if<</amber>> / <<amber>>else<</amber>>. <<amber>>for<</amber>> / <<amber>>while<</amber>>
  / <<amber>>for...of<</amber>>. Curly braces are required for blocks; semicolons end
  statements. <<amber>>===<</amber>> is strict equality (no type coercion); use it.
  <<amber>>==<</amber>> coerces and produces surprises.

      <<amber>>for<</amber>> (<<amber>>const<</amber>> item <<amber>>of<</amber>> cars) {
          console.log(item)
      }

# FUNCTIONS

  Two declaration styles. <<amber>>function<</amber>> for hoisted top-level definitions.
  Arrow functions for callbacks and anywhere lexical <<bold>>this<</bold>> matters.

      <<amber>>function<</amber>> <<teal>>total_with_tax<</teal>>(amount, rate=<<blue>>0.08<</blue>>) {
          <<amber>>return<</amber>> amount * (<<blue>>1<</blue>> + rate)
      }
      <<amber>>const<</amber>> double = x => x * <<blue>>2<</blue>>

  Default parameters go after <<amber>>=<</amber>> in the signature. Arrow functions
  inherit <<bold>>this<</bold>> from their enclosing scope; regular functions don't.

# ARRAY METHODS

  <<bold>>.map<</bold>>, <<bold>>.filter<</bold>>, <<bold>>.reduce<</bold>> are the workhorses. They
  return new arrays (or values) without mutating the original. Chain them.

      <<amber>>const<</amber>> open_costs = orders
          .<<purple>>filter<</purple>>(o => o.status === <<green>>'Open'<</green>>)
          .<<purple>>map<</purple>>(o => o.cost)

  <<dim>>Filter narrows; map transforms. See <<qid:js_am_09>>.<</dim>>

# DESTRUCTURING

  Pull values out of arrays and objects with one statement.

      <<amber>>const<</amber>> [x, y] = [<<blue>>3<</blue>>, <<blue>>4<</blue>>]                    <<dim>>array form<</dim>>
      <<amber>>const<</amber>> { name, phone } = customer    <<dim>>object form<</dim>>

  Rename with <<bold>>{ name: customer_name }<</bold>>. Set defaults with
  <<bold>>{ name = 'unknown' }<</bold>>. Combines with function parameters.

# TEMPLATE LITERALS

  Backticks (not quotes) for interpolation. Multi-line strings work.

      <<green>>`Welcome to ${shop_name}, you have ${count} jobs open.`<</green>>

# CLASSES

  <<amber>>class<</amber>> declares a type. <<bold>>constructor<</bold>> runs at construction.
  <<bold>>this<</bold>> is the instance. <<amber>>extends<</amber>> for inheritance; <<amber>>super<</amber>>
  calls the parent.

      <<amber>>class<</amber>> <<teal>>WorkOrder<</teal>> {
          <<teal>>constructor<</teal>>(id, cost, status) {
              this.id = id
              this.cost = cost
              this.status = status
          }
          <<teal>>is_open<</teal>>() { <<amber>>return<</amber>> this.status === <<green>>'Open'<</green>> }
      }

  <<purple>>get<</purple>> and <<purple>>set<</purple>> declare property accessors that look like
  attributes from the outside. Useful for derived properties.

# ASYNC

  <<amber>>Promise<</amber>> represents a future value. <<amber>>async<</amber>> declares a
  function that returns a Promise. <<amber>>await<</amber>> unwraps one inside an
  async function. <<amber>>Promise.all<</amber>> runs Promises in parallel.

      <<amber>>const<</amber>> [x, y] = <<amber>>await<</amber>> Promise.<<purple>>all<</purple>>([fetch_a(), fetch_b()])

  Wrap <<amber>>await<</amber>> in <<amber>>try<</amber>>/<<amber>>catch<</amber>> for rejection handling
  — a rejected Promise inside <<amber>>await<</amber>> throws synchronously.

# JSON

  <<amber>>JSON.parse<</amber>>(str) converts a JSON string to a value.
  <<amber>>JSON.stringify<</amber>>(v) converts back. The two roundtrip cleanly for
  plain data; functions and undefined values are dropped.

# GENERATORS AND ITERATION

  <<amber>>function*<</amber>> declares a generator. <<amber>>yield<</amber>> produces a value
  and pauses. Lazy by default — only computes what's consumed.

      <<amber>>function*<</amber>> <<teal>>range_gen<</teal>>(s, e) {
          <<amber>>for<</amber>> (<<amber>>let<</amber>> i = s; i < e; i++) <<amber>>yield<</amber>> i
      }

  <<bold>>[...gen()]<</bold>> or <<bold>>Array.from(gen())<</bold>> materializes the sequence.

# MODERN PATTERNS

  Spread <<bold>>...arr<</bold>> unpacks arrays; rest <<bold>>...args<</bold>> gathers them.
  <<amber>>Map<</amber>> and <<amber>>Set<</amber>> are real collections beyond plain objects.
  <<amber>>Object.entries<</amber>> / <<amber>>Object.values<</amber>> iterate object data.
  <<amber>>Optional chaining<</amber>> <<bold>>obj?.x?.y<</bold>> safely reads through nulls.

# TAG REFERENCE

  <<amber>>amber<</amber>> keywords. <<teal>>teal<</teal>> callables/types. <<green>>green<</green>>
  strings. <<blue>>blue<</blue>> numerics. <<purple>>purple<</purple>> methods/decorators.
  <<red>>red<</red>> warnings. <<dim>>dim<</dim>> asides. <<bold>>bold<</bold>> emphasis.
