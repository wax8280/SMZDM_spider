# -*- coding: utf-8 -*-
import re


class TempliteSyntaxError(ValueError):
    pass


class CodeBuilder(object):
    """代码生成器"""

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def __str__(self):
        return "".join(unicode(c) for c in self.code)

    def add_line(self, line):
        """
        生成一行新的代码，它会根据当前的缩进自动进行代码的缩进和换行。

        """
        self.code.extend([" " * self.indent_level, line, "\n"])

    def add_section(self):
        """
        生成一个新的CodeBuilder类。将当前列表code的代码连接成字符串（自动调用__str__方法），
        放入新的CodeBuilder类中，返回新的CodeBuilder类。
        """
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    # 根据Python的PEP8规范，规定一个缩进等于4个空格
    INDENT_STEP = 4

    def indent(self):
        """indent和dedent方法，分别增加与减少缩进"""
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """indent和dedent方法，分别增加与减少缩进"""
        self.indent_level -= self.INDENT_STEP

    def get_globals(self):
        """
        get_globals函数，执行code的代码（在我们的模板引擎中，也就是定义一个函数。），
        返回一个名为global_namespace的字典，里面包含有刚定义的函数。


        如下面的代码中，global_namespace[‘SEVENTEEN’]就是数字17，
        global_namespace[‘three’]就是刚定义的函数three。

        python_source = '''
            \ SEVENTEEN = 17
                def three():return 3
            '''
        global_namespace = {}
        exec(python_source, global_namespace)

        """

        assert self.indent_level == 0
        python_source = str(self)
        global_namespace = {}
        exec (python_source, global_namespace)
        return global_namespace


class Templite(object):
    """一个类似Django的简单的模板引擎

    访问变量的属性或方法::

        {{var.modifer.modifier|filter|filter}}

    循环::

        {% for var in list %}...{% endfor %}

    条件判断::

        {% if var %}...{% endif %}

    注释::

        {# This will be ignored #}

    我通过向Template的构造函数传入模板，产生一个实例，我们就完成了编译。
    之后我们可以多次调用render方法渲染，从而得到不同的结果。

        templite = Templite('''
            <h1>Hello {{name|upper}}!</h1>
            {% for topic in topics %}
                <p>You are interested in {{topic}}.</p>
            {% endif %}
            ''',
            {'upper': str.upper},
        )
        text = templite.render({
            'name': "Ned",
            'topics': ['Python', 'Geometry', 'Juggling'],
        })

    """

    def __init__(self, text, *contexts):

        # 构造函数接收一个字符串以及多个变量
        # （这些变量可以是函数，也可以是列表，字符串等在模板里面要用到的东西），
        # 将多个变量放入内部定义的context字典中

        self.context = {}
        for context in contexts:
            self.context.update(context)

        # 集合all_vars存放所有模板里面出现的变量，
        # 集合loop_vars存放模板循环里面（如for循环）里面出现的变量。
        self.all_vars = set()
        self.loop_vars = set()

        # 使用CodeBuilder
        code = CodeBuilder()

        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_unicode = unicode")

        buffered = []

        def flush_output():
            """
            把buffered里面的Python语句通过CodeBuilder的add_line方法
            添加到CodeBuilder实例的code列表中。
            """
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                code.add_line("extend_result([%s])" % ", ".join(buffered))
            del buffered[:]

        # 我们想要确认这些语句是否正确。我们就需要一个栈。
        # 当我们遇到一个{% if .. %}标签的时候。我们把“if”push进栈；
        # 当我们遇到{% endif %}的时候，我们pop栈，如果没有“if”在栈顶的话，将会报错。
        ops_stack = []


        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)
        # r表示raw_string；?s说明“.”匹配任何东西，包括换行符；
        # {{.*?}}，{%.*?%}，{#.*?#}分别匹配表达式，条件判断与循环语句，注释。
        #
        # 如果，有如下模板：
        # <p>Topics for {{name}}: {% for t in topics %}{{t}}, {% endfor %}</p>
        # 我们把它分割成：
        #     [
        #     '<p>Topics for ',
        #     '{{name}}',
        #     ': ',
        #     '{% for t in topics %}',
        #     '',
        #     '{{t}}',
        #     ', ',
        #     '{% endfor %}',
        #     '</p>'
        #     ]

        for token in tokens:
            if token.startswith('{#'):
                # 第一种情况是注释，我们直接忽略。
                continue

            elif token.startswith('{{'):
                # 对于{{…}}，我们砍掉两对大括号，忽略前后的空格，把里面的语句提取出来。然后把它传递给_expr_code方法。
                # _expr_code方法会把我们模板的表达式转化成Python的表达式。
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_unicode(%s)" % expr)

            elif token.startswith('{%'):
                # 第三种情况就是{% … %}，首先我们运行flush_output函数
                # 通过CodeBuilder的add_line方法把buffered里面的Python语句添加到CodeBuilder实例的code列表中。
                flush_output()
                words = token[2:-2].strip().split()

                # 现在我们对于if，for或者end这三种情况分别作出不同的处理。
                if words[0] == 'if':
                    # if标签通常只有一个表达式，所以对于长度不符的情况，我们使用_syntax_error方法抛出一个错误。
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    # 我们把“if”压进栈 ops_stack，以便我们检查endif标签。
                    ops_stack.append('if')
                    code.add_line("if %s:" % self._expr_code(words[1]))
                    code.indent()

                elif words[0] == 'for':
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    # 方法_variable的作用除了检查变量是否有非法字符外，还会将变量添加到集合中。
                    # for..in的in后面可能跟的是一个变量，亦或是一个可迭代的表达式（如 for i in range(10)）。所以我们要使用_expr_code方法。
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                            "for c_%s in %s:" % (
                                words[1],
                                self._expr_code(words[3])
                            )
                    )
                    code.indent()
                elif words[0].startswith('end'):
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else:
                    # 对于不可识别的，我们通过_syntax_error方法抛出错误
                    self._syntax_error("Don't understand tag", words[0])
            else:
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            # ops_stack的值应为空的
            self._syntax_error("Unmatched action tag", ops_stack[-1])

        flush_output()

        # 把在all_vars集合 而不在loop_vars集合里面的变量找出来。
        # 把context里面的变量解包出来，放入加上“c_”前缀的同名变量中。
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line("c_%s = context[%r]" % (var_name, var_name))

        code.add_line("return ''.join(result)")
        code.dedent()
        self._render_function = code.get_globals()['render_function']

    def _expr_code(self, expr):
        """。_expr_code将模板中的表达式编译成Python中的表达式。"""
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
        elif "." in expr:
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

    def _syntax_error(self, msg, thing):
        """抛出一个异常"""
        raise TempliteSyntaxError("%s: %r" % (msg, thing))

    def _variable(self, name, vars_set):
        """检查变量是否有非法字符，将变量添加到集合中。"""
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def render(self, context=None):
        """
        这里的self.context是一个包含需要用来渲染模板的动态数据和过滤器函数的字典。
        我们在Template类的构造函数里面已经update过，
        一般来说我们在Template类的构造函数里update的是过滤器的函数；
        在方法render里面update的是用来渲染模板的动态数据。
        因为创建了一个Template实例出来就说明编译完成。
        调用render，通过传入不同的context实现不同的渲染。
        """
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots):
        """在编译阶段，模板表达式如x.y.z被编译成do_dots(x, ‘y’, ‘z’) """
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
