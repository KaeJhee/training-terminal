# PYTHON · TIER 4 CONCEPTS (EXPERIENCED)

  <<dim>>Object-oriented building blocks plus the standard-library data structures
  that make data wrangling a one-liner.<</dim>>

# CLASSES

  A class defines a type. An instance is an object of that type. The
  <<bold>>__init__<</bold>> method runs at construction time. <<bold>>self<</bold>> is the
  current instance, passed implicitly when you call a method on an object.

      <<amber>>class<</amber>> <<teal>>WorkOrder<</teal>>:
          <<amber>>def<</amber>> <<teal>>__init__<</teal>>(self, id, cost, status):
              self.id = id
              self.cost = cost
              self.status = status
          <<amber>>def<</amber>> <<teal>>is_open<</teal>>(self):
              <<amber>>return<</amber>> self.status == <<green>>'Open'<</green>>

  Construct with <<bold>>WorkOrder(1, 100, 'Open')<</bold>>. Call methods with
  <<bold>>order.is_open()<</bold>>. Attributes are accessed with dot notation.

# INHERITANCE

  <<amber>>class<</amber>> Child(Parent) inherits Parent's attributes and methods. Add
  new methods or override existing ones. <<bold>>super()<</bold>> calls the parent's
  version when you need to extend rather than replace.

      <<amber>>class<</amber>> <<teal>>SportsCar<</teal>>(<<teal>>Vehicle<</teal>>):
          <<amber>>def<</amber>> <<teal>>is_fast<</teal>>(self):
              <<amber>>return<</amber>> <<amber>>True<</amber>>

  <<dim>>Inheritance is one of three ways to share code (composition and
  duck-typing are the others). Use it when the relationship is genuinely
  "is-a." A SportsCar is-a Vehicle. A Customer is not-a Address.<</dim>>

# DUNDER METHODS

  Methods named <<bold>>__name__<</bold>> hook into Python syntax. <<bold>>__str__<</bold>>
  controls what <<amber>>str<</amber>>(obj) returns. <<bold>>__repr__<</bold>> controls
  <<amber>>repr<</amber>>(obj). <<bold>>__eq__<</bold>> controls <<bold>>==<</bold>>. There are dozens.

      <<amber>>def<</amber>> <<teal>>__str__<</teal>>(self):
          <<amber>>return<</amber>> <<green>>f'Mechanic: {self.name}'<</green>>

# DECORATORS ON METHODS

  <<purple>>@property<</purple>> turns a method into a read-only attribute. The caller
  uses <<bold>>obj.tax<</bold>> not <<bold>>obj.tax()<</bold>>.

      <<purple>>@property<</purple>>
      <<amber>>def<</amber>> <<teal>>tax<</teal>>(self):
          <<amber>>return<</amber>> self.cost * <<blue>>0.08<</blue>>

  <<purple>>@staticmethod<</purple>> removes the implicit <<bold>>self<</bold>>. Use it for
  utility functions that logically belong on the class but don't need
  instance state.

# EXCEPTIONS

  <<amber>>try<</amber>> runs a block. <<amber>>except<</amber>> catches a specific exception
  class. <<amber>>else<</amber>> runs if no exception. <<amber>>finally<</amber>> runs either way.

      <<amber>>try<</amber>>:
          result = a / b
      <<amber>>except<</amber>> <<red>>ZeroDivisionError<</red>>:
          result = <<amber>>None<</amber>>

  <<red>>Bare except: catches everything including KeyboardInterrupt<</red>>. Always
  catch the specific class.

# COLLECTIONS LIBRARY

  <<bold>>Counter<</bold>> tallies hashable items. Pass it an iterable, get back a
  dict-like with counts.

      <<amber>>from<</amber>> collections <<amber>>import<</amber>> <<teal>>Counter<</teal>>
      <<teal>>Counter<</teal>>([<<green>>'red'<</green>>, <<green>>'blue'<</green>>, <<green>>'red'<</green>>])
      <<dim>>Counter({'red': 2, 'blue': 1})<</dim>>

  <<bold>>defaultdict(int)<</bold>> is a dict that creates default values on missing
  keys, replacing the <<bold>>if k not in d: d[k] = 0<</bold>> dance. Pass any
  zero-arg callable: <<amber>>int<</amber>> (gives 0), <<amber>>list<</amber>> (gives []),
  <<amber>>set<</amber>> (gives set()).

# ENUMERATE

  <<amber>>enumerate<</amber>>(iter) yields (index, item) pairs. Cleaner than running
  your own counter alongside the loop.

      <<amber>>for<</amber>> i, item <<amber>>in<</amber>> <<amber>>enumerate<</amber>>(items):
          <<amber>>print<</amber>>(i, item)

  NEXT TIER: generators, decorators, closures, recursion, <<amber>>functools<</amber>>
  tricks. Anything that treats functions themselves as values to compose.

---

# EXAMPLE 1

  A class that combines <<bold>>__init__<</bold>>, a regular method, and a
  <<purple>>@property<</purple>>. This is the canonical "domain object" shape.

      <<amber>>class<</amber>> <<teal>>Order<</teal>>:
          <<amber>>def<</amber>> <<teal>>__init__<</teal>>(self, cost, status):
              self.cost = cost
              self.status = status
          <<purple>>@property<</purple>>
          <<amber>>def<</amber>> <<teal>>tax<</teal>>(self):
              <<amber>>return<</amber>> self.cost * <<blue>>0.08<</blue>>
          <<amber>>def<</amber>> <<teal>>is_open<</teal>>(self):
              <<amber>>return<</amber>> self.status == <<green>>'Open'<</green>>

      o = <<teal>>Order<</teal>>(<<blue>>100<</blue>>, <<green>>'Open'<</green>>)
      <<amber>>print<</amber>>(o.tax)         <<dim>>8.0    (no parens, it's a property)<</dim>>
      <<amber>>print<</amber>>(o.is_open())   <<dim>>True   (parens, it's a method)<</dim>>

# EXAMPLE 2

  Tally a list with Counter, then read the most common entries. Replaces
  twenty lines of dict bookkeeping.

      <<amber>>from<</amber>> collections <<amber>>import<</amber>> <<teal>>Counter<</teal>>
      tags = [<<green>>'open'<</green>>, <<green>>'open'<</green>>, <<green>>'closed'<</green>>, <<green>>'open'<</green>>, <<green>>'wip'<</green>>]
      counts = <<teal>>Counter<</teal>>(tags)
      <<amber>>print<</amber>>(counts)               <<dim>>Counter({'open': 3, 'closed': 1, 'wip': 1})<</dim>>
      <<amber>>print<</amber>>(counts.most_common(<<blue>>2<</blue>>))  <<dim>>[('open', 3), ('closed', 1)]<</dim>>

  <<dim>>Counter is the data structure that powers most "frequency analysis"
  tasks: word counts, label distributions, bag-of-words features.<</dim>>

# EXAMPLE 3

  Generators, previewing the next tier. Right now you build a list eagerly:

      <<amber>>def<</amber>> <<teal>>first_n_squares<</teal>>(n):
          result = []
          <<amber>>for<</amber>> i <<amber>>in<</amber>> <<amber>>range<</amber>>(<<blue>>1<</blue>>, n + <<blue>>1<</blue>>):
              result.append(i * i)
          <<amber>>return<</amber>> result

  <<dim>>At Master tier you'll use <</dim>><<amber>>yield<</amber>><<dim>> to produce values
  lazily, one at a time:

  <</dim>>      <<amber>>def<</amber>> <<teal>>squares<</teal>>(n):
          <<amber>>for<</amber>> i <<amber>>in<</amber>> <<amber>>range<</amber>>(<<blue>>1<</blue>>, n + <<blue>>1<</blue>>):
              <<amber>>yield<</amber>> i * i

  <<dim>>The generator computes each value on demand. It uses constant memory
  even for huge n, and you can pipe it through other iterators without
  materializing the whole list. See <</dim>><<qid:py_mas_03>><<dim>>.<</dim>>
