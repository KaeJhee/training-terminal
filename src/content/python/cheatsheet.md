# PYTHON CHEATSHEET

  <<dim>>A working reference for the whole language. Skim it once, come back when stuck.<</dim>>

# VARIABLES AND TYPES

  No declaration keyword. Bind a name with <<amber>>=<</amber>>. Python infers the type
  from the value.

      garage = <<green>>'Terminal Auto'<</green>>
      count  = <<blue>>42<</blue>>
      rate   = <<blue>>0.075<</blue>>
      active = <<amber>>True<</amber>>

  Strings, ints, floats, bools, <<amber>>None<</amber>>. Convert between them with
  <<amber>>int<</amber>>(), <<amber>>float<</amber>>(), <<amber>>str<</amber>>(), <<amber>>bool<</amber>>().
  <<dim>>Conversions can fail at runtime. See <<qid:py_intro_09>>.<</dim>>

# COLLECTIONS

  Four built-ins handle most needs. Pick by access pattern.

      cars   = [<<green>>'Skyline'<</green>>, <<green>>'Supra'<</green>>]            <<dim>>list:  ordered, mutable<</dim>>
      coords = (<<blue>>3<</blue>>, <<blue>>4<</blue>>)                            <<dim>>tuple: ordered, immutable<</dim>>
      tags   = {<<green>>'jdm'<</green>>, <<green>>'turbo'<</green>>}                <<dim>>set:   unordered, unique<</dim>>
      car    = {<<green>>'make'<</green>>: <<green>>'Nissan'<</green>>, <<green>>'year'<</green>>: <<blue>>1996<</blue>>}     <<dim>>dict:  key -> value<</dim>>

  Index with <<bold>>obj[i]<</bold>>. Slice with <<bold>>obj[a:b]<</bold>>. Length with
  <<amber>>len<</amber>>(obj). Membership with <<amber>>in<</amber>>.

# CONTROL FLOW

  <<amber>>if<</amber>> / <<amber>>elif<</amber>> / <<amber>>else<</amber>> for branching. <<amber>>for<</amber>> /
  <<amber>>while<</amber>> for loops. Indentation is syntactic. Four spaces is the
  standard.

      <<amber>>for<</amber>> item <<amber>>in<</amber>> cars:
          <<amber>>print<</amber>>(item)

      <<amber>>if<</amber>> count > <<blue>>0<</blue>>:
          <<amber>>print<</amber>>(<<green>>'positive'<</green>>)
      <<amber>>elif<</amber>> count == <<blue>>0<</blue>>:
          <<amber>>print<</amber>>(<<green>>'zero'<</green>>)
      <<amber>>else<</amber>>:
          <<amber>>print<</amber>>(<<green>>'negative'<</green>>)

# FUNCTIONS

  <<amber>>def<</amber>> declares one. Default arguments go after required ones.
  <<amber>>return<</amber>> sends a value back; without it, the function returns
  <<amber>>None<</amber>>.

      <<amber>>def<</amber>> <<teal>>total_with_tax<</teal>>(amount, rate=<<blue>>0.08<</blue>>):
          <<amber>>return<</amber>> amount * (<<blue>>1<</blue>> + rate)

  Lambdas are one-line anonymous functions. Useful as arguments to
  <<amber>>sorted<</amber>>, <<amber>>map<</amber>>, <<amber>>filter<</amber>>.

      sorted_people = <<amber>>sorted<</amber>>(people, key=<<amber>>lambda<</amber>> p: p[<<green>>'age'<</green>>])

# COMPREHENSIONS

  Build a list, dict, or set from an iterable in one expression. Equivalent
  to a for-loop with append, but tighter and faster.

      squares  = [x**<<blue>>2<</blue>> <<amber>>for<</amber>> x <<amber>>in<</amber>> <<amber>>range<</amber>>(<<blue>>5<</blue>>)]
      lookup   = {k: <<amber>>len<</amber>>(k) <<amber>>for<</amber>> k <<amber>>in<</amber>> words}
      uniques  = {x.lower() <<amber>>for<</amber>> x <<amber>>in<</amber>> tags}

  <<dim>>Comprehensions replace the loop-and-append pattern. See <<qid:py_int_01>>.<</dim>>

# CLASSES

  <<amber>>class<</amber>> declares a type. <<bold>>__init__<</bold>> is the constructor.
  <<bold>>self<</bold>> is the instance.

      <<amber>>class<</amber>> <<teal>>WorkOrder<</teal>>:
          <<amber>>def<</amber>> <<teal>>__init__<</teal>>(self, id, cost, status):
              self.id, self.cost, self.status = id, cost, status
          <<amber>>def<</amber>> <<teal>>is_open<</teal>>(self):
              <<amber>>return<</amber>> self.status == <<green>>'Open'<</green>>

  Decorators on methods: <<purple>>@property<</purple>> makes it look like an attribute,
  <<purple>>@staticmethod<</purple>> removes the implicit self.

# ERRORS

  <<amber>>try<</amber>> / <<amber>>except<</amber>> catches exceptions. Catch the specific class.
  Bare <<amber>>except<</amber>> is a code smell.

      <<amber>>try<</amber>>:
          result = a / b
      <<amber>>except<</amber>> <<red>>ZeroDivisionError<</red>>:
          result = <<amber>>None<</amber>>

# IMPORTS AND STDLIB

  <<amber>>from<</amber>> module <<amber>>import<</amber>> thing. <<bold>>collections<</bold>> gives you
  <<amber>>Counter<</amber>>, <<amber>>defaultdict<</amber>>, <<amber>>namedtuple<</amber>>.
  <<bold>>functools<</bold>> gives you <<amber>>reduce<</amber>>, <<purple>>@lru_cache<</purple>>.
  <<bold>>dataclasses<</bold>> gives you <<purple>>@dataclass<</purple>> for boilerplate-free
  record types.

# F-STRINGS

  Format with values inline. <<bold>>:.2f<</bold>> formats a float to two decimals.
  <<bold>>,<</bold>> adds thousand separators.

      <<green>>f'Price: ${price:.2f}'<</green>>
      <<green>>f'Count: {count:,}'<</green>>

# TAG REFERENCE

  <<amber>>amber<</amber>> keywords/builtins. <<teal>>teal<</teal>> callables/types. <<green>>green<</green>>
  strings. <<blue>>blue<</blue>> numerics. <<purple>>purple<</purple>> decorators. <<red>>red<</red>>
  warnings/exceptions. <<dim>>dim<</dim>> asides. <<bold>>bold<</bold>> emphasis.
